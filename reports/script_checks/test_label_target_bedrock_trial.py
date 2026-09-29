"""Offline tests: never call AWS/OpenAI."""
import copy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "lama/generateDataset"))
import label_target_bedrock_trial as trial


def fixture():
    job = {"job_id": "r000002_v00", "case_name": "original", "jumlah_pesan": 1,
           "source": {"source_row": 2, "source_group": "sample", "label_intent": "defend", "teks_chat": "Aku bukan Hitman."}}
    item = {"job_id": job["job_id"], "session": {"case_name": "original", "participants": ["Budi"], "focus_player": "Budi", "panggilan": [],
            "messages": [{"pengirim": "Budi", "teks_chat": "Aku bukan Hitman.", "label_intent": "defend",
                          "target": [{"pemain": "Budi", "relasi": "defend", "bukti_pesan": [1]}]}]}}
    return job, item


def response(items, reason="end_turn"):
    return {"stopReason": reason, "usage": {"inputTokens": 1000, "outputTokens": 2000},
            "output": {"message": {"content": [{"text": json.dumps({"results": items})}]}}}


class BedrockTrialTests(unittest.TestCase):
    def test_fifty_cover_all_cases_and_exclude_completed(self):
        jobs = trial.base.plan_jobs(trial.base.read_source(ROOT / "ai_2_dataset_baru/data/dataset_final3.csv"), 1)
        selected = trial.select_jobs(jobs, 50)
        self.assertEqual(len({j["job_id"] for j in selected}), 50)
        self.assertEqual({j["case_name"] for j in selected}, set(trial.base.CASES))
        self.assertEqual({j["source"]["label_intent"] for j in selected}, {"offend", "defend", "neutral"})
        self.assertEqual(selected, trial.select_jobs(jobs, 50))
        job, item = fixture()
        with tempfile.TemporaryDirectory() as d:
            trial.dump(Path(d) / (job["job_id"] + ".json"), {"job": job, "session": item["session"], "model_verification_passed": True})
            self.assertEqual(trial.remaining_jobs([job], Path(d)), [])
            changed = {**job, "case_name": "explicit"}
            self.assertEqual(trial.remaining_jobs([changed], Path(d)), [changed])

    def test_exactly_one_call_no_model_verification_and_no_false_pass(self):
        job, item = fixture()
        calls = []
        def sender(request):
            calls.append(request)
            return response([item])
        with tempfile.TemporaryDirectory() as d, patch.object(trial.base, "verify_session", side_effect=AssertionError("Verifier must never run")):
            directory = Path(d)
            result = trial.run_once(directory, {}, [job], sender)
            self.assertEqual(len(calls), 1)
            self.assertEqual(result["accepted_local_structure"], 1)
            self.assertEqual(result["cost"]["usd_before_tax"], "0.011")
            saved = json.loads((directory / (job["job_id"] + ".json")).read_text())
            self.assertFalse(saved["model_verification_passed"])
            group = json.loads((directory / "draft.groups.jsonl").read_text())
            self.assertFalse(group["model_verification_passed"])
            with self.assertRaises(FileExistsError):
                trial.run_once(directory, {}, [job], sender)
            self.assertEqual(len(calls), 1)

    def test_timeout_never_retries_or_leaks_exception_secrets(self):
        job, _ = fixture()
        calls = []
        def fail(request):
            calls.append(request)
            raise TimeoutError("secret-example-token")
        with tempfile.TemporaryDirectory() as d:
            directory = Path(d)
            with self.assertRaisesRegex(RuntimeError, "No retry"):
                trial.run_once(directory, {}, [job], fail)
            self.assertEqual(len(calls), 1)
            self.assertNotIn("secret-example-token", (directory / "failure.json").read_text())
            self.assertTrue((directory / "attempt.json").exists())

    def test_duplicate_or_unknown_ids_quarantine_batch(self):
        job, item = fixture()
        with self.assertRaises(ValueError):
            trial.validate_results({"results": [item, item]}, [job])
        item["job_id"] = "unknown"
        with self.assertRaises(ValueError):
            trial.validate_results({"results": [item]}, [job])

    def test_bad_evidence_rejected_valid_items_preserved_and_missing_reported(self):
        job, item = fixture()
        badjob = copy.deepcopy(job)
        badjob["job_id"] = "bad"
        bad = copy.deepcopy(item)
        bad["job_id"] = "bad"
        bad["session"]["messages"][0]["target"][0]["bukti_pesan"] = [2]
        missing = dict(job, job_id="missing")
        accepted, rejected = trial.validate_results({"results": [bad, item]}, [job, badjob, missing])
        self.assertEqual([x["job"]["job_id"] for x in accepted], [job["job_id"]])
        self.assertEqual({x["job_id"] for x in rejected}, {"bad", "missing"})

    def test_truncated_output_keeps_usage_without_export(self):
        job, item = fixture()
        with tempfile.TemporaryDirectory() as d:
            directory = Path(d)
            with self.assertRaises(RuntimeError):
                trial.run_once(directory, {}, [job], lambda request: response([item], "max_tokens"))
            self.assertTrue((directory / "usage_cost.json").exists())
            self.assertTrue((directory / "response.json").exists())
            self.assertFalse((directory / "draft.csv").exists())

    def test_missing_usage_does_not_fabricate_cost(self):
        self.assertIsNone(trial.cost_from_usage({})["usd_before_tax"])
        self.assertIsNone(trial.cost_from_usage({"inputTokens": 5, "outputTokens": 6, "cacheReadInputTokens": 10})["usd_before_tax"])


if __name__ == "__main__":
    unittest.main()
