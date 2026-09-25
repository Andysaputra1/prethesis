"""Jalankan konfigurasi IndoBERT yang sama dengan notebook pada semua versi.

Contoh: venv/Scripts/python.exe -u scripts/tune_indobert.py --versions ai_1_nlu_v3_600
Tanpa --versions, kelima versi dijalankan berurutan pada satu GPU.
"""

import argparse
import gc
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lama.modules.nlu_training import train_transformer


DATASETS = {
    "ai_1_nlu_v3_600": "chat_dataset2 copy.csv",
    "ai_1_nlu_v3_300": "v3_chat_dataset2_300.csv",
    "ai_1_nlu_v2_200": "v2_chat_dataset_200.csv",
    "ai_1_nlu_v2_100": "v2_chat_dataset_100.csv",
    "ai_1_nlu_v1": "v1_chat_dataset_100.csv",
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--versions", nargs="+", choices=DATASETS, default=list(DATASETS))
    args = parser.parse_args()
    import torch
    from datasets import disable_progress_bars

    disable_progress_bars()
    report_path = ROOT / "reports" / "indobert_tuning_results.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    results = json.loads(report_path.read_text(encoding="utf-8")) if report_path.exists() else {}
    for version in args.versions:
        started = time.perf_counter()
        model_dir = ROOT / version / "models"
        previous_path = model_dir / "intent_classifier_transformer" / "metrics.json"
        previous = json.loads(previous_path.read_text(encoding="utf-8")) if previous_path.exists() else None
        # Simpan konteks hasil terdahulu sebelum file model digantikan hasil baru.
        previous_summary = model_dir / "intent_classifier_transformer" / "training_summary.json"
        previous_protocol = "validation_selection" if previous_summary.exists() else "legacy_test_selection"
        results[version] = {
            "status": "running", "previous_metrics": previous,
            "previous_protocol": previous_protocol,
        }
        report_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
        print(f"\nRUN VERSION: {version}", flush=True)
        result = train_transformer(
            ROOT / version / "data" / DATASETS[version], model_dir,
            epochs=12, learning_rates=(1e-5, 2e-5, 3e-5), device="cuda",
        )
        summary = result["training_summary"]
        results[version].update({
            "status": "completed", "metrics": result["metrics"],
            "training_summary": summary,
            "elapsed_seconds": round(time.perf_counter() - started, 1),
        })
        report_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
        print(f"COMPLETED {version}: test macro-F1={result['metrics']['f1_macro']}", flush=True)
        del result
        gc.collect()
        torch.cuda.empty_cache()


if __name__ == "__main__":
    main()
