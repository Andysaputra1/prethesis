"""Ekspor kurva trial terpilih dan tabel hasil dari laporan tuning IndoBERT."""

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


def main():
    directory = Path(__file__).resolve().parents[1] / "reports"
    results = json.loads((directory / "indobert_tuning_results.json").read_text(encoding="utf-8"))
    completed = {key: value for key, value in results.items() if value["status"] == "completed"}
    if not completed:
        raise SystemExit("Belum ada versi yang selesai dilatih.")
    fig, axes = plt.subplots(len(completed), 2, figsize=(12, 3.3 * len(completed)), squeeze=False)
    rows = []
    for index, (version, result) in enumerate(sorted(completed.items())):
        summary = result["training_summary"]
        best = summary["best_trial"]
        trial = next(t for t in summary["trials"] if t["trial"] == best["trial"])
        training = [row for row in trial["history"] if "loss" in row]
        validation = [row for row in trial["history"] if "eval_f1_macro" in row]
        loss_ax, f1_ax = axes[index]
        loss_ax.plot([r["epoch"] for r in training], [r["loss"] for r in training], "o-", label="Training loss")
        loss_ax.plot([r["epoch"] for r in validation], [r["eval_loss"] for r in validation], "o-", label="Validation loss")
        f1_ax.plot([r["epoch"] for r in validation], [r["eval_f1_macro"] for r in validation], "o-", color="#19836d", label="Validation macro-F1")
        for ax in (loss_ax, f1_ax):
            ax.axvline(best["best_epoch"], linestyle="--", color="#777777", label="Selected epoch")
            ax.set_xlabel("Epoch")
            ax.grid(alpha=0.2)
            ax.legend(fontsize=8)
        loss_ax.set_title(f"{version.removeprefix('ai_1_nlu_')} | selected LR = {best['learning_rate']:g}")
        loss_ax.set_ylabel("Loss")
        f1_ax.set_title(f"Best validation macro-F1 = {best['best_validation_f1_macro']:.4f}")
        f1_ax.set_ylabel("Macro-F1")
        f1_ax.set_ylim(0, 1)
        rows.append({
            "version": version, **summary["split_sizes"],
            "learning_rate": best["learning_rate"], "best_epoch": best["best_epoch"],
            "epochs_trained": best["epochs_trained"],
            "validation_macro_f1": best["best_validation_f1_macro"],
            "test_accuracy": result["metrics"]["accuracy"],
            "test_macro_f1": result["metrics"]["f1_macro"],
        })
    fig.suptitle("IndoBERT: selected trial per dataset (selection uses validation only)", fontsize=13)
    fig.tight_layout(rect=(0, 0, 1, 0.98))
    for extension in ("png", "pdf"):
        fig.savefig(directory / f"indobert_learning_curves.{extension}", dpi=170, bbox_inches="tight")
    plt.close(fig)
    pd.DataFrame(rows).to_csv(directory / "indobert_results.csv", index=False)
    print(pd.DataFrame(rows).to_string(index=False))


if __name__ == "__main__":
    main()
