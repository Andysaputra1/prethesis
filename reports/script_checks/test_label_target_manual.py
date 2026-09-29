"""Uji alur manual ChatGPT/Gemini tanpa memanggil API."""
import csv
import json
import sys
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "lama/generateDataset"))
import label_target_manual as manual


def job(job_id, case, label, text, count):
    return {"job_id": job_id, "case_name": case, "case_description": manual.lt.CASES[case],
            "source": {"source_row": 2, "source_group": "g", "teks_chat": text, "label_intent": label},
            "context_limit": 12, "jumlah_pesan": count, "pesan_typo_ringan": []}


def session(case, sender, text, label, targets):
    return {"case_name": case, "participants": ["Budi", "Andi"], "focus_player": "", "panggilan": [],
            "messages": [{"pengirim": sender, "teks_chat": text, "label_intent": label, "target": targets}]}


class ManualFlowTests(unittest.TestCase):
    def test_extract_json_ignores_surrounding_text(self):
        text = 'Berikut hasilnya:\n```json\n{"results": []}\n```\nSemoga membantu.'
        self.assertEqual(manual.extract_json(text), {"results": []})
        self.assertEqual(manual.extract_json('{"results": [1]}'), {"results": [1]})

    def test_prompts_hide_variation_source_text(self):
        with tempfile.TemporaryDirectory() as d:
            source = Path(d) / "sumber.csv"
            with source.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=["teks_chat", "label_intent"])
                writer.writeheader()
                writer.writerows([{"teks_chat": f"Teks rahasia {i}", "label_intent": "offend"} for i in range(3)])
            folder = Path(d) / "manual"
            manual.cmd_prompts(Namespace(input=source, dir=folder, per_case=None, batch_size=4))
            prompts = sorted((folder / "prompt").glob("*.txt"))
            self.assertEqual(len(prompts), 2)
            sent = [j for p in prompts for j in json.loads(p.read_text(encoding="utf-8").split("\nJOBS:\n")[1])["jobs"]]
            for item in sent:
                self.assertEqual("teks_chat" in item["source"], item["case_name"] == "original")
            with self.assertRaises(SystemExit):
                manual.cmd_prompts(Namespace(input=source, dir=folder, per_case=None, batch_size=4))

    def test_import_saves_valid_retries_invalid_and_exports(self):
        good = job("r000002_v00", "original", "defend", "Aku bukan Hitman.", 1)
        bad = job("r000002_v01", "explicit", "offend", "Aku bukan Hitman.", 1)
        with tempfile.TemporaryDirectory() as d:
            folder = Path(d)
            (folder / "hasil").mkdir()
            (folder / "jobs.json").write_text(json.dumps([good, bad]), encoding="utf-8")
            results = {"results": [
                {"job_id": good["job_id"], "session": session("original", "Budi", "Aku bukan Hitman.", "defend",
                                                             [{"pemain": "Budi", "relasi": "defend", "bukti_pesan": [1]}])},
                {"job_id": bad["job_id"], "session": session("explicit", "Budi", "Dia pasti Hitman.", "offend",
                                                            [{"pemain": "tidak_diketahui", "relasi": "offend", "bukti_pesan": []}])},
            ]}
            (folder / "hasil" / "001_gemini.txt").write_text("Ini jawabannya:\n```json\n" + json.dumps(results) + "\n```", encoding="utf-8")
            manual.cmd_import(Namespace(dir=folder, batch_size=10))
            self.assertTrue((folder / "sessions" / "r000002_v00.json").exists())
            self.assertFalse((folder / "sessions" / "r000002_v01.json").exists())
            retry = (folder / "prompt_ulang" / "ulang_001.txt").read_text(encoding="utf-8")
            self.assertIn("kesalahan_sebelumnya", retry)
            self.assertIn("eksplisit", retry)
            self.assertIn("gemini: 1 lolos, 1 gagal", (folder / "laporan.md").read_text(encoding="utf-8"))
            manual.cmd_export(Namespace(dir=folder, output=folder / "hasil.csv"))
            with (folder / "hasil.csv").open(encoding="utf-8") as handle:
                self.assertEqual(len(list(csv.DictReader(handle))), 1)


if __name__ == "__main__":
    unittest.main()
