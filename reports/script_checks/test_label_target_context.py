"""Checks lokal dengan data buatan dan API tiruan; main generator tidak dijalankan."""

import ast
import copy
import csv
import importlib.util
import json
import tempfile
import struct
import threading
import unittest
import zlib
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "lama/generateDataset/label_target.py"
spec = importlib.util.spec_from_file_location("label_target_context", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def relation(player, label, evidence):
    return {"pemain": player, "relasi": label, "bukti_pesan": evidence}


def message(speaker, text, label="neutral", targets=None):
    return {"pengirim": speaker, "teks_chat": text, "label_intent": label, "target": targets or []}


def fixture(case="memory_outside_window"):
    messages = [
        message("Citra", "Andy pasti Hitman.", "offend", [relation("Andy", "offend", [1])]),
        message("Budi", "Bukan dia.", "defend", [relation("Andy", "defend", [1])]),
    ]
    messages += [message("Citra", f"Waktu diskusi tersisa {60 - i} detik.") for i in range(11)]
    messages.append(message("Budi", "Bukan, dia tidak bersalah.", "defend", [relation("Andy", "defend", [2])]))
    if case == "outside_window_unknown":
        messages[1] = message("Budi", "Sekarang kita bahas aturan waktu saja.")
        messages[-1]["target"] = [relation("tidak_diketahui", "defend", [])]
    session = {
        "case_name": case, "participants": ["Andy", "Budi", "Citra"],
        "focus_player": "Andy", "messages": messages,
    }
    source = {"source_row": 2, "source_group": "group1", "teks_chat": "Aku yakin bukan Andy.", "label_intent": "defend"}
    job = {"job_id": "r000002_v01", "case_name": case, "source": source}
    return session, job


# Frame application/vnd.amazon.eventstream seperti yang dikirim Bedrock ConverseStream.
def stream_frame(event_type, payload, message_type="event"):
    headers = b""
    kind = ":event-type" if message_type == "event" else ":exception-type"
    for name, value in [(kind, event_type), (":message-type", message_type), (":content-type", "application/json")]:
        name, value = name.encode(), value.encode()
        headers += bytes([len(name)]) + name + bytes([7]) + struct.pack(">H", len(value)) + value
    body = json.dumps(payload).encode()
    prelude = struct.pack(">II", 16 + len(headers) + len(body), len(headers))
    message = prelude + struct.pack(">I", zlib.crc32(prelude)) + headers + body
    return message + struct.pack(">I", zlib.crc32(message))


def stream_response(text, stop_reason, usage):
    data = b"".join([
        stream_frame("messageStart", {"role": "assistant"}),
        stream_frame("contentBlockDelta", {"contentBlockIndex": 0, "delta": {"text": text[:len(text) // 2]}}),
        stream_frame("contentBlockDelta", {"contentBlockIndex": 0, "delta": {"text": text[len(text) // 2:]}}),
        stream_frame("messageStop", {"stopReason": stop_reason}),
        stream_frame("metadata", {"usage": usage, "metrics": {"latencyMs": 1}}),
    ])
    # Potongan kecil menguji penyambungan frame yang tiba terpisah.
    return SimpleNamespace(status_code=200, iter_content=lambda chunk_size=None: [data[i:i + 7] for i in range(0, len(data), 7)])


class PassingVerifier:
    def __init__(self):
        self.payloads = []

    def invoke(self, messages):
        self.payloads.append(json.loads(messages[1][1]))
        return SimpleNamespace(valid=True, issues=[])


class ContextDatasetTests(unittest.TestCase):
    def test_syntax_and_no_old_review_fields(self):
        source = SCRIPT.read_text(encoding="utf-8")
        ast.parse(source)
        self.assertNotIn("needs_review", source)
        self.assertEqual(module.FIELDS, ["pengirim", "teks_chat", "label_intent", "chat_sebelumnya", "daftar_pemain", "target"])

    def test_memory_resolves_target_outside_raw_window(self):
        session, job = fixture()
        module.validate_session(session, job)
        record = module.make_record(session)
        self.assertEqual(len(record["chat_sebelumnya"]), 12)
        self.assertNotIn("Andy", " ".join(m["teks_chat"] for m in record["chat_sebelumnya"]))
        self.assertEqual(record["target"], [{"pemain": "Andy", "relasi": "defend"}])
        self.assertEqual(record["chat_sebelumnya"][0]["target"], record["target"])
        self.assertNotIn("bukti_pesan", json.dumps(record))

    def test_missing_memory_remains_unknown(self):
        session, job = fixture("outside_window_unknown")
        module.validate_session(session, job)
        self.assertEqual(module.make_record(session)["target"][0]["pemain"], "tidak_diketahui")

    def test_future_evidence_rejected(self):
        session, job = fixture()
        session["messages"][0]["target"][0]["bukti_pesan"] = [2]
        with self.assertRaisesRegex(ValueError, "masa depan"):
            module.validate_session(session, job)

    def test_direct_evidence_outside_window_rejected(self):
        session, job = fixture()
        session["messages"][-1]["target"][0]["bukti_pesan"] = [1]
        with self.assertRaisesRegex(ValueError, "di luar jendela"):
            module.validate_session(session, job)

    def test_causal_verifier_never_sees_future(self):
        session, _ = fixture()
        verifier = PassingVerifier()
        module.verify_session(session, verifier)
        self.assertEqual(len(verifier.payloads), 14)
        for index, payload in enumerate(verifier.payloads):
            expected = [module.visible_message(m) for m in session["messages"][max(0, index - 12):index]]
            self.assertEqual(payload["chat_sebelumnya"], expected)
            self.assertEqual(payload["pesan_sekarang"], module.visible_message(session["messages"][index]))

    def test_verifier_failure_stops(self):
        class Reject:
            def invoke(self, messages):
                return SimpleNamespace(valid=False, issues=["Target tidak didukung"])
        with self.assertRaisesRegex(ValueError, "Verifikasi pesan 1"):
            module.verify_session(fixture()[0], Reject())

    def test_original_preserves_text_and_uses_empty_context(self):
        session, job = fixture()
        job["case_name"] = session["case_name"] = "original"
        session["messages"] = [
            message("Citra", job["source"]["teks_chat"], "defend", [relation("Andy", "defend", [1])])
        ]
        module.validate_session(session, job)
        self.assertEqual(module.make_record(session)["chat_sebelumnya"], [])
        session["messages"][0]["teks_chat"] = "teks berubah"
        with self.assertRaises(ValueError):
            module.validate_session(session, job)

    def test_self_and_mixed_relations(self):
        session, job = fixture()
        job["case_name"] = session["case_name"] = "self"
        session["messages"] = [message("Budi", "Aku bukan Hitman.", "defend", [relation("Budi", "defend", [1])])]
        module.validate_session(session, job)
        session["case_name"] = job["case_name"] = "mixed_relations"
        job["source"]["label_intent"] = "offend"
        session["messages"] = [message(
            "Citra", "Budi bukan Hitman, justru Andy pelakunya.", "offend",
            [relation("Budi", "defend", [1]), relation("Andy", "offend", [1])],
        )]
        module.validate_session(session, job)
        self.assertEqual(len(module.make_record(session)["target"]), 2)

    def test_neutral_has_no_relations(self):
        session, job = fixture()
        session["case_name"] = job["case_name"] = "neutral_names"
        job["source"]["label_intent"] = "neutral"
        session["messages"] = [message("Citra", "Andy, sisa waktunya berapa?")]
        module.validate_session(session, job)
        self.assertEqual(module.make_record(session)["target"], [])
        session["messages"][0]["target"] = [relation("Andy", "offend", [1])]
        with self.assertRaises(ValueError):
            module.validate_session(session, job)

    def test_export_roundtrip_exactly_six_columns(self):
        session, job = fixture()
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "sample.csv"
            groups = Path(directory) / "sample.groups.jsonl"
            module.export_records([{"job": job, "session": session}], output, groups)
            with output.open(encoding="utf-8", newline="") as handle:
                reader = csv.DictReader(handle)
                rows = list(reader)
            self.assertEqual(reader.fieldnames, module.FIELDS)
            self.assertEqual(json.loads(rows[0]["target"]), module.make_record(session)["target"])
            self.assertEqual(len(json.loads(rows[0]["chat_sebelumnya"])), 12)
            self.assertEqual(json.loads(rows[0]["daftar_pemain"]), session["participants"])
            self.assertEqual(json.loads(groups.read_text())["source_group"], "group1")
            with self.assertRaises(FileExistsError):
                module.export_records([], output, groups)

    def test_case_schedule_covers_all_cases_and_keeps_groups(self):
        rows = []
        for label in ["offend", "defend", "neutral"]:
            for index in range(30):
                rows.append({"label_intent": label, "source_row": len(rows) + 2, "source_group": f"{label}_{index}", "teks_chat": label})
        jobs = module.plan_jobs(rows, 1)
        self.assertEqual(len(jobs), 180)
        self.assertEqual(set(job["case_name"] for job in jobs), set(module.CASES))
        for index in range(0, len(jobs), 2):
            self.assertEqual(jobs[index]["source"]["source_group"], jobs[index + 1]["source"]["source_group"])

    def test_generate_batch_uses_one_request_for_fifty_jobs(self):
        session, job = fixture()
        jobs = [{**job, "job_id": f"job_{i}"} for i in range(50)]
        payloads = []
        class FakeGenerator:
            def invoke(self, messages):
                payload = json.loads(messages[1][1])
                payloads.append(payload)
                # Return in reverse order to ensure mapping uses IDs, not positions.
                return SimpleNamespace(model_dump=lambda: {"results": [
                    {"job_id": task["job_id"], "session": copy.deepcopy(session)}
                    for task in reversed(payload["jobs"])
                ]})
        accepted = {}
        module.generate_batch(jobs, FakeGenerator(), PassingVerifier(), 2,
                              lambda task, result: accepted.update({task["job_id"]: result}), lambda phase: None)
        self.assertEqual(len(payloads), 1)
        self.assertEqual(len(payloads[0]["jobs"]), 50)
        self.assertEqual(set(accepted), {job["job_id"] for job in jobs})

    def test_batch_retries_only_failed_examples(self):
        session, job = fixture()
        jobs = [{**job, "job_id": name} for name in ["good", "bad"]]
        requests = []
        class FakeGenerator:
            def invoke(self, messages):
                payload = json.loads(messages[1][1])
                requests.append([j["job_id"] for j in payload["jobs"]])
                results = []
                for task in payload["jobs"]:
                    result = copy.deepcopy(session)
                    if len(requests) == 1 and task["job_id"] == "bad":
                        result["messages"][-1]["target"][0]["bukti_pesan"] = [99]
                    results.append({"job_id": task["job_id"], "session": result})
                return SimpleNamespace(model_dump=lambda: {"results": results})
        accepted = []
        module.generate_batch(jobs, FakeGenerator(), PassingVerifier(), 2,
                              lambda task, result: accepted.append(task["job_id"]), lambda phase: None)
        self.assertEqual(requests, [["good", "bad"], ["bad"]])
        self.assertEqual(accepted, ["good", "bad"])

    def test_batch_without_verifier_accepts_after_local_checks(self):
        session, job = fixture()
        jobs = [{**job, "job_id": name} for name in ["good", "bad"]]
        requests = []
        class FakeGenerator:
            def invoke(self, messages):
                payload = json.loads(messages[1][1])
                requests.append([j["job_id"] for j in payload["jobs"]])
                results = []
                for task in payload["jobs"]:
                    result = copy.deepcopy(session)
                    if len(requests) == 1 and task["job_id"] == "bad":
                        result["messages"][-1]["target"][0]["bukti_pesan"] = [99]
                    results.append({"job_id": task["job_id"], "session": result})
                return SimpleNamespace(model_dump=lambda: {"results": results})
        accepted = []
        module.generate_batch(jobs, FakeGenerator(), None, 2,
                              lambda task, result: accepted.append(task["job_id"]), lambda phase: None)
        self.assertEqual(requests, [["good", "bad"], ["bad"]])
        self.assertEqual(accepted, ["good", "bad"])

    def test_batch_rejects_duplicate_ids(self):
        session, job = fixture()
        class FakeGenerator:
            def invoke(self, messages):
                item = {"job_id": job["job_id"], "session": session}
                return SimpleNamespace(model_dump=lambda: {"results": [item, item]})
        accepted = []
        with self.assertRaisesRegex(ValueError, "duplikat"):
            module.generate_batch([job], FakeGenerator(), PassingVerifier(), 1,
                                  lambda task, result: accepted.append(task), lambda phase: None)
        self.assertEqual(accepted, [])

    def test_five_batches_run_together_without_duplicate_jobs(self):
        barrier = threading.Barrier(5)
        lock = threading.Lock()
        visited = []
        running = 0
        peak = 0
        batches = [list(range(i * 50, (i + 1) * 50)) for i in range(11)]

        def worker(number, batch):
            nonlocal running, peak
            with lock:
                running += 1
                peak = max(peak, running)
            if number <= 5:
                barrier.wait(timeout=5)
            with lock:
                visited.extend(batch)
                running -= 1

        module.run_batches(batches, worker, 5)
        self.assertEqual(peak, 5)
        self.assertEqual(sorted(visited), list(range(550)))

    def test_opening_and_exact_short_histories_for_all_intents(self):
        for label in ["offend", "defend", "neutral"]:
            for count in range(4):
                case = "first_message" if count == 0 else f"short_history_{count}"
                with self.subTest(label=label, context_count=count):
                    session, job = fixture()
                    session["case_name"] = job["case_name"] = case
                    job["source"]["label_intent"] = label
                    history = [message("Citra", "Andy itu Hitman.", "offend", [relation("Andy", "offend", [1])])]
                    history += [message("Citra", "Waktu diskusinya masih cukup.")] * 2
                    texts = {"offend": "Aku curiga Andy.", "defend": "Andy bukan Hitman.", "neutral": "Halo, kita mulai diskusinya."}
                    targets = [] if label == "neutral" else [relation("Andy", label, [count + 1])]
                    session["messages"] = history[:count] + [message("Budi", texts[label], label, targets)]
                    module.validate_session(session, job)
                    record = module.make_record(session)
                    self.assertEqual(len(record["chat_sebelumnya"]), count)
                    verifier = PassingVerifier()
                    module.verify_session(session, verifier)
                    self.assertEqual(len(verifier.payloads[-1]["chat_sebelumnya"]), count)
                    # A padded history must not pass as a shorter-history case.
                    session["messages"].insert(-1, message("Citra", "Oke."))
                    with self.assertRaises(ValueError):
                        module.validate_session(session, job)

    def test_opening_unknown_and_self_without_context(self):
        for label in ["offend", "defend"]:
            for case in ["first_message_unknown", "first_message_self"]:
                with self.subTest(label=label, case=case):
                    session, job = fixture()
                    session["case_name"] = job["case_name"] = case
                    job["source"]["label_intent"] = label
                    if case == "first_message_unknown":
                        text = "Dia Hitman." if label == "offend" else "Dia bukan Hitman."
                        targets = [relation("tidak_diketahui", label, [])]
                    else:
                        text = "Vote aku saja, aku pelakunya." if label == "offend" else "Aku bukan Hitman."
                        targets = [relation("Budi", label, [1])]
                    session["messages"] = [message("Budi", text, label, targets)]
                    module.validate_session(session, job)
                    self.assertEqual(module.make_record(session)["chat_sebelumnya"], [])

    def test_roster_alone_cannot_resolve_opening_pronoun(self):
        session, job = fixture()
        session["case_name"] = job["case_name"] = "first_message_unknown"
        session["messages"] = [message("Budi", "Dia bukan Hitman.", "defend", [relation("Andy", "defend", [1])])]
        with self.assertRaisesRegex(ValueError, "jejak identitas"):
            module.validate_session(session, job)

    def test_rejected_context_annotation_stops_before_main_message(self):
        class RejectSecond(PassingVerifier):
            def invoke(self, messages):
                super().invoke(messages)
                if len(self.payloads) == 2:
                    return SimpleNamespace(valid=False, issues=["Target pesan konteks salah"])
                return SimpleNamespace(valid=True, issues=[])

        verifier = RejectSecond()
        with self.assertRaisesRegex(ValueError, "Verifikasi pesan 2 gagal"):
            module.verify_session(fixture()[0], verifier)
        self.assertEqual(len(verifier.payloads), 2)
        self.assertTrue(verifier.payloads[0]["teks_sintetis"])

    def test_short_history_can_contain_same_sender_and_earlier_reference(self):
        session, job = fixture()
        session["case_name"] = job["case_name"] = "short_history_3"
        session["messages"] = [
            message("Citra", "Andy itu Hitman.", "offend", [relation("Andy", "offend", [1])]),
            message("Budi", "Waktunya masih cukup."),
            message("Budi", "Kita lanjut diskusinya."),
            message("Budi", "Orang yang dituduh tadi bukan Hitman.", "defend", [relation("Andy", "defend", [1])]),
        ]
        module.validate_session(session, job)
        self.assertEqual(module.make_record(session)["target"], [{"pemain": "Andy", "relasi": "defend"}])

    def test_every_early_case_is_scheduled_for_eligible_labels(self):
        common = {"first_message", "short_history_1", "short_history_2", "short_history_3"}
        for label in ["offend", "defend", "neutral"]:
            rows = [{"source_row": i + 2, "source_group": str(i), "teks_chat": label, "label_intent": label} for i in range(40)]
            cases = {job["case_name"] for job in module.plan_jobs(rows, 1)}
            expected = common if label == "neutral" else common | {"first_message_unknown", "first_message_self"}
            self.assertTrue(expected.issubset(cases))

    def test_spelling_slots_are_about_one_and_a_half_percent(self):
        rows = [{"source_row": i + 2, "source_group": str(i), "teks_chat": "teks", "label_intent": ["offend", "defend", "neutral"][i % 3]} for i in range(1000)]
        jobs = module.plan_jobs(rows, 1)
        synthetic = [job for job in jobs if job["case_name"] != "original"]
        total = sum(min(13, job["jumlah_pesan"]) for job in synthetic)
        marked = sum(len(job["pesan_typo_ringan"]) for job in synthetic)
        self.assertEqual(marked, total // 67)
        self.assertTrue(0.01 <= marked / total <= 0.02)
        for job in jobs:
            self.assertTrue(all(max(1, job["jumlah_pesan"] - 12) <= i <= job["jumlah_pesan"] for i in job["pesan_typo_ringan"]))
            if job["case_name"] == "original":
                self.assertEqual(job["pesan_typo_ringan"], [])

    def test_spelling_slot_is_passed_only_to_correct_message_verifier(self):
        session, job = fixture()
        job["pesan_typo_ringan"] = [2]
        verifier = PassingVerifier()
        module.verify_session(session, verifier, job)
        self.assertEqual(verifier.payloads[1]["gaya_pesan"], "satu_typo_atau_singkatan")
        self.assertTrue(all(payload["gaya_pesan"] == "ejaan_jelas" for i, payload in enumerate(verifier.payloads) if i != 1))

    def _case(self, case, label, participants, messages):
        session, job = fixture()
        session["case_name"] = job["case_name"] = case
        job["source"]["label_intent"] = label
        session["participants"] = participants
        session["messages"] = messages
        return session, job

    def test_new_cases_accept_valid_and_reject_missing_pattern(self):
        roster = ["Andy", "Budi", "Citra", "Dodi"]
        accusation = message("Citra", "Andy sama Dodi dari tadi saling nutupin.", "offend",
                             [relation("Andy", "offend", [1]), relation("Dodi", "offend", [1])])
        cases = {
            "agreement": ("offend", [accusation, message("Budi", "Setuju, aku juga ngerasa gitu.", "offend",
                                                          [relation("Andy", "offend", [1])])],
                          "Setuju, Andy memang aneh.", "menyebut ulang"),
            "plural_reference": ("offend", [accusation, message("Budi", "Mereka berdua mencurigakan banget.", "offend",
                                                                 [relation("Andy", "offend", [1]), relation("Dodi", "offend", [1])])],
                                 "Dua orang itu mencurigakan banget.", "jamak"),
            "rhetorical_question": ("offend", [message("Budi", "Andy, kenapa kamu diam terus dari tadi?", "offend",
                                                       [relation("Andy", "offend", [1])])],
                                    "Andy pasti Hitman.", "retoris"),
            "stance_change": ("defend", [message("Budi", "Aku curiga Andy.", "offend", [relation("Andy", "offend", [1])]),
                                         message("Citra", "Hmm, lanjut dulu."),
                                         message("Budi", "Setelah dipikir, Andy bukan Hitman deh.", "defend",
                                                 [relation("Andy", "defend", [3])])],
                              None, "berubah sikap"),
        }
        for case, (label, messages, bad_text, error) in cases.items():
            with self.subTest(case=case):
                session, job = self._case(case, label, roster, copy.deepcopy(messages))
                module.validate_session(session, job)
                if bad_text:
                    session["messages"][-1]["teks_chat"] = bad_text
                else:
                    session["messages"][0]["pengirim"] = "Dodi"
                with self.assertRaisesRegex(ValueError, error):
                    module.validate_session(session, job)

    def test_plural_reference_needs_two_players(self):
        session, job = self._case("plural_reference", "offend", ["Andy", "Budi", "Citra"], [
            message("Citra", "Andy dari tadi ngeles.", "offend", [relation("Andy", "offend", [1])]),
            message("Budi", "Mereka mencurigakan.", "offend", [relation("Andy", "offend", [1])]),
        ])
        with self.assertRaisesRegex(ValueError, "dua pemain"):
            module.validate_session(session, job)

    def test_existing_cases_must_show_their_pattern(self):
        roster = ["Andy", "Budi", "Citra"]
        bad = {
            "explicit": ("offend", [message("Budi", "Dia pasti Hitman.", "offend", [relation("tidak_diketahui", "offend", [])])]),
            "negation": ("defend", [message("Budi", "Andy orang baik.", "defend", [relation("Andy", "defend", [1])])]),
            "witness": ("offend", [message("Budi", "Andy pasti Hitman.", "offend", [relation("Andy", "offend", [1])])]),
            "second_person": ("offend", [message("Budi", "Andy pasti Hitman.", "offend", [relation("Andy", "offend", [1])])]),
            "neutral_after_accusation": ("neutral", [message("Citra", "Halo semua."), message("Budi", "Sisa waktu berapa?")]),
        }
        for case, (label, messages) in bad.items():
            with self.subTest(case=case):
                session, job = self._case(case, label, roster, messages)
                with self.assertRaises(ValueError):
                    module.validate_session(session, job)

    def test_offend_relation_requires_offend_intent_except_original_text(self):
        roster = ["Andy", "Budi", "Citra"]
        relations = [relation("Citra", "defend", [1]), relation("Andy", "offend", [1])]
        session, job = self._case("explicit", "defend", roster, [
            message("Citra", "Aku bukan Hitman, Andy yang aneh.", "defend", relations)])
        with self.assertRaisesRegex(ValueError, "berintent offend"):
            module.validate_session(session, job)
        session, job = self._case("original", "defend", roster, [
            message("Citra", "Aku bukan Hitman, Andy yang aneh.", "defend", copy.deepcopy(relations))])
        job["source"]["teks_chat"] = "Aku bukan Hitman, Andy yang aneh."
        module.validate_session(session, job)

    def test_same_player_cannot_be_offended_and_defended(self):
        session, job = self._case("mixed_relations", "offend", ["Andy", "Budi", "Citra"], [
            message("Budi", "Andy bukan Hitman, tapi Andy aneh.", "offend",
                    [relation("Andy", "defend", [1]), relation("Andy", "offend", [1])])])
        with self.assertRaisesRegex(ValueError, "sekaligus"):
            module.validate_session(session, job)

    def test_second_person_resolved_by_previous_sender(self):
        session, job = self._case("second_person", "offend", ["Andy", "Budi", "Citra"], [
            message("Andy", "Vote siapa aja terserah."),
            message("Budi", "Kamu kok santai banget, jelas kamu Hitman.", "offend", [relation("Andy", "offend", [1])]),
        ])
        module.validate_session(session, job)

    def test_persistent_failure_reports_each_job(self):
        session, job = fixture()
        jobs = [{**job, "job_id": name} for name in ["good", "bad"]]
        class FakeGenerator:
            def invoke(self, messages):
                payload = json.loads(messages[1][1])
                results = []
                for task in payload["jobs"]:
                    result = copy.deepcopy(session)
                    if task["job_id"] == "bad":
                        result["messages"][-1]["target"][0]["bukti_pesan"] = [99]
                    results.append({"job_id": task["job_id"], "session": result})
                return SimpleNamespace(model_dump=lambda: {"results": results})
        accepted = []
        with self.assertRaises(module.BatchFailure) as caught:
            module.generate_batch(jobs, FakeGenerator(), None, 2,
                                  lambda task, result: accepted.append(task["job_id"]), lambda phase: None)
        self.assertEqual(accepted, ["good"])
        self.assertEqual(list(caught.exception.errors), ["bad"])
        self.assertIn("masa depan", caught.exception.errors["bad"])

    def test_alias_must_resemble_its_player_only(self):
        self.assertTrue(module.alias_fits("ndy", "Andy"))
        self.assertTrue(module.alias_fits("andi", "Andy"))
        self.assertTrue(module.alias_fits("DK", "DarkKnight"))
        self.assertFalse(module.alias_fits("budi", "Andy"))
        for roster, alias in [(["Andy", "Budi"], "dia"), (["Andy", "Budi"], "aja"), (["Andy", "Andre"], "And"),
                              (["Andy", "Budi"], "budi"), (["Andy", "Budi"], "cipto")]:
            with self.subTest(alias=alias):
                session = {"participants": roster, "panggilan": [{"pemain": "Andy", "sebutan": [alias]}]}
                with self.assertRaisesRegex(ValueError, "Panggilan"):
                    module.read_aliases(session)

    def test_nickname_case_links_alias_to_real_name(self):
        roster = ["Andy", "Budi", "Citra"]
        for label, text, targets in [
            ("offend", "ndy dari tadi ngeles terus, aku curiga.", [relation("Andy", "offend", [1])]),
            ("neutral", "ndy udah vote belum?", []),
        ]:
            with self.subTest(label=label):
                session, job = self._case("nickname", label, roster, [message("Budi", text, label, targets)])
                session["panggilan"] = [{"pemain": "Andy", "sebutan": ["ndy"]}]
                module.validate_session(session, job)
                self.assertEqual(module.make_record(session)["daftar_pemain"], roster)
        session["panggilan"] = []
        with self.assertRaisesRegex(ValueError, "panggilan"):
            module.validate_session(session, job)
        session, job = self._case("nickname", "offend", roster, [
            message("Budi", "ndy dari tadi ngeles.", "offend", [relation("Andy", "offend", [1])])])
        with self.assertRaisesRegex(ValueError, "jejak identitas"):
            module.validate_session(session, job)

    def test_variation_must_not_copy_source_text(self):
        session, job = self._case("explicit", "offend", ["Andy", "Budi", "Citra"], [
            message("Budi", "Aku curiga Andy!", "offend", [relation("Andy", "offend", [1])])])
        job["source"]["teks_chat"] = "aku curiga andy"
        with self.assertRaisesRegex(ValueError, "menyalin teks sumber"):
            module.validate_session(session, job)
        session["messages"][-1]["teks_chat"] = "Andy dari tadi ngeles, aku curiga dia."
        module.validate_session(session, job)

    def test_only_original_jobs_send_source_text(self):
        rows = [{"source_row": 2, "source_group": "g", "teks_chat": "Aku curiga Andy.", "label_intent": "offend"}]
        original, variation = module.plan_jobs(rows, 1)
        self.assertEqual(module.job_for_model(original)["source"]["teks_chat"], "Aku curiga Andy.")
        sent = module.job_for_model(variation)
        self.assertNotIn("teks_chat", sent["source"])
        self.assertEqual(sent["source"]["label_intent"], "offend")
        self.assertIn(sent["topik"], module.VARIATION_TOPICS)
        self.assertEqual(variation["source"]["teks_chat"], "Aku curiga Andy.")

    def test_per_case_pilot_is_subset_with_balanced_labels(self):
        rows = [{"source_row": i + 2, "source_group": str(i), "teks_chat": "teks",
                 "label_intent": ["offend", "offend", "defend", "neutral"][i % 4]} for i in range(400)]
        jobs = module.plan_jobs(rows, 1)
        pilot = module.select_per_case(jobs, 10)
        counts = {case: sum(j["case_name"] == case for j in pilot) for case in module.CASES}
        self.assertTrue(all(0 < n <= 10 for n in counts.values()))
        self.assertTrue(all(job in jobs for job in pilot))
        explicit = [j["source"]["label_intent"] for j in pilot if j["case_name"] == "explicit"]
        available = sum(j["case_name"] == "explicit" and j["source"]["label_intent"] == "defend" for j in jobs)
        # Label jarang diambil sebanyak mungkin sampai separuh kuota; sisanya diisi label lain.
        self.assertEqual(explicit.count("defend"), min(available, 5))
        self.assertEqual(len(explicit), 10)
        self.assertEqual(pilot, module.select_per_case(jobs, 10))

    def test_event_stream_parser_checks_crc_and_reports_exceptions(self):
        data = stream_frame("contentBlockDelta", {"delta": {"text": "halo"}})
        events = list(module.read_event_stream([data[:5], data[5:]]))
        self.assertEqual(events[0][0][":event-type"], "contentBlockDelta")
        self.assertEqual(events[0][1]["delta"]["text"], "halo")
        with self.assertRaisesRegex(ValueError, "CRC"):
            list(module.read_event_stream([data[:-1] + bytes([data[-1] ^ 1])]))
        failing = SimpleNamespace(status_code=200, iter_content=lambda chunk_size=None: [
            stream_frame("throttlingException", {"message": "Too many tokens"}, "exception")])
        with self.assertRaises(module.BedrockHTTPError) as caught:
            module.converse_stream(lambda url, **kwargs: failing, "url", "secret", {})
        self.assertEqual(caught.exception.status, "throttlingException")

    def test_bedrock_generator_parses_retries_and_counts_tokens(self):
        session, job = fixture()
        good = json.dumps({"results": [{"job_id": job["job_id"], "session": {**session, "panggilan": []}}]})
        replies = [
            SimpleNamespace(status_code=429, json=lambda: {"message": "slow down"}),
            stream_response(good, "end_turn", {"inputTokens": 10, "outputTokens": 20}),
            stream_response('{"results": [{"job_id"', "max_tokens", {"inputTokens": 5, "outputTokens": 7}),
        ]
        calls = []
        def post(url, **kwargs):
            calls.append(kwargs["json"])
            return replies.pop(0)
        batch_result, _ = module.build_schemas()
        totals = module.TokenTotals()
        generator = module.BedrockGenerator("model-x", "us-east-1", "secret", batch_result, 1000, 0.3, totals, post=post)
        with patch.object(module.time, "sleep"):
            first = generator.invoke([("system", "sys"), ("human", "{}")]).model_dump()
            truncated = generator.invoke([("system", "sys"), ("human", "{}")]).model_dump()
        self.assertEqual(first["results"][0]["job_id"], job["job_id"])
        self.assertEqual(truncated["results"], [])
        self.assertEqual((totals.input, totals.output), (15, 27))
        self.assertEqual(len(calls), 3)
        self.assertEqual(calls[0]["outputConfig"]["textFormat"]["type"], "json_schema")

    def test_new_models_skip_temperature_and_accept_effort(self):
        inference, extra = module.bedrock_request_options("global.anthropic.claude-fable-5-1", 1000, 0.3, "low")
        self.assertEqual(inference, {"maxTokens": 1000})
        self.assertEqual(extra, {"output_config": {"effort": "low"}})
        inference, extra = module.bedrock_request_options("us.anthropic.claude-sonnet-4-6", 1000, 0.3)
        self.assertEqual(inference, {"maxTokens": 1000, "temperature": 0.3})
        self.assertEqual(extra, {})

    def test_reference_focus_only_at_case_position(self):
        messages = [message("Citra", "Andy mencurigakan.", "offend", [relation("Andy", "offend", [1])])]
        messages += [message("Citra", f"Sisa waktu {60 - i} detik.") for i in range(11)]
        messages.append(message("Budi", "Dia bukan Hitman.", "defend", [relation("Andy", "defend", [1])]))
        session, job = self._case("reference_start", "defend", ["Andy", "Budi", "Citra"], messages)
        session["focus_player"] = "Andy"
        module.validate_session(session, job)
        session["messages"][4]["teks_chat"] = "Andy tadi ke mana?"
        with self.assertRaisesRegex(ValueError, "di luar posisi"):
            module.validate_session(session, job)

    def test_original_letter_ids_must_be_players(self):
        text = "gw curiga sama si D, jawabannya muter terus"
        session, job = self._case("original", "offend", ["Bambang", "Danang"], [
            message("Bambang", text, "offend", [relation("tidak_diketahui", "offend", [])])])
        job["source"]["teks_chat"] = text
        with self.assertRaisesRegex(ValueError, "ID pemain berhuruf"):
            module.validate_session(session, job)
        session["participants"] = ["Bambang", "D"]
        session["messages"][0]["target"] = [relation("D", "offend", [1])]
        module.validate_session(session, job)

    def test_typo_alias_keeps_first_letter(self):
        roster = ["Andika", "Bela", "Fani"]
        self.assertEqual(module.read_aliases({"participants": roster, "panggilan": [
            {"pemain": "Andika", "sebutan": ["Andi", "ndi"]}]}), {"Andika": ["Andi", "ndi"]})
        self.assertFalse(module.alias_fits("Andi", "Fani"))

    def test_alias_in_window_breaks_memory_case(self):
        session, job = fixture()
        session["panggilan"] = [{"pemain": "Andy", "sebutan": ["ndy"]}]
        module.validate_session(session, job)
        session["messages"][5]["teks_chat"] = "ndy tadi ke mana?"
        with self.assertRaisesRegex(ValueError, "memori luar jendela"):
            module.validate_session(session, job)


if __name__ == "__main__":
    unittest.main()
