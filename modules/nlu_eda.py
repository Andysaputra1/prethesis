"""EDA dan pembersihan data bersama untuk klasifikasi intent game HOSTAGE.

Dataset NLU hanya memakai dua kolom yang memang tersedia saat prediksi:
``teks_chat`` dan ``label_intent``. Fungsi di sini tidak memakai role asli
atau hasil aksi malam, sehingga tidak menciptakan data leakage ke model.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


TEXT_COLUMN = "teks_chat"
LABEL_COLUMN = "label_intent"
REQUIRED_COLUMNS = {TEXT_COLUMN, LABEL_COLUMN}
LEGACY_GAME_PATTERN = r"(?i)\b(?:shadow\s*heist|brankas\w*|koin\w*|uang\w*|budget\w*|tebus\w*|beli\s+item\w*|polisi\w*|gangster\w*)"


def load_clean_nlu_dataset(dataset_path: str | Path) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Baca, validasi, dan bersihkan dataset intent secara deterministik.

    Duplikat tepat dihapus. Jika satu teks sama memiliki lebih dari satu
    label, seluruh teks konflik dikeluarkan karena akan mengajari model dua
    jawaban berbeda untuk input yang identik.
    """
    path = Path(dataset_path)
    if not path.is_file():
        raise FileNotFoundError(f"Dataset tidak ditemukan: {path}")

    raw = pd.read_csv(path)
    missing_columns = REQUIRED_COLUMNS.difference(raw.columns)
    if missing_columns:
        raise ValueError(
            f"Dataset harus punya kolom {sorted(REQUIRED_COLUMNS)}; "
            f"yang tidak ada: {sorted(missing_columns)}"
        )

    report: dict[str, Any] = {
        "dataset_path": str(path),
        "rows_raw": len(raw),
        "missing_cells_raw": int(raw[list(REQUIRED_COLUMNS)].isna().sum().sum()),
    }
    clean = raw[[TEXT_COLUMN, LABEL_COLUMN]].dropna().copy()
    clean[TEXT_COLUMN] = clean[TEXT_COLUMN].astype(str).str.replace(r"\s+", " ", regex=True).str.strip()
    clean[LABEL_COLUMN] = clean[LABEL_COLUMN].astype(str).str.strip().str.lower()

    empty_mask = (clean[TEXT_COLUMN] == "") | (clean[LABEL_COLUMN] == "")
    report["empty_rows_removed"] = int(empty_mask.sum())
    clean = clean.loc[~empty_mask].copy()

    # HOSTAGE adalah Zero Economy. Baris dari game lama tidak ikut melatih
    # classifier, tetapi CSV sumber sengaja tidak ditulis ulang di sini.
    legacy_mask = clean[TEXT_COLUMN].str.contains(LEGACY_GAME_PATTERN, regex=True, na=False)
    report["legacy_context_rows_removed"] = int(legacy_mask.sum())
    clean = clean.loc[~legacy_mask].copy()

    report["exact_duplicates_removed"] = int(clean.duplicated([TEXT_COLUMN, LABEL_COLUMN]).sum())
    clean = clean.drop_duplicates([TEXT_COLUMN, LABEL_COLUMN]).copy()

    label_count_per_text = clean.groupby(TEXT_COLUMN)[LABEL_COLUMN].nunique()
    conflicting_texts = label_count_per_text[label_count_per_text > 1].index
    report["conflicting_texts_removed"] = int(len(conflicting_texts))
    if len(conflicting_texts):
        clean = clean.loc[~clean[TEXT_COLUMN].isin(conflicting_texts)].copy()

    class_counts = clean[LABEL_COLUMN].value_counts().sort_index()
    if clean.empty:
        raise ValueError("Tidak ada data valid setelah pembersihan dataset.")
    if class_counts.min() < 2:
        too_small = class_counts[class_counts < 2].to_dict()
        raise ValueError(f"Setiap intent perlu minimal 2 sampel untuk split stratified: {too_small}")

    report.update(
        {
            "rows_clean": len(clean),
            "class_count": int(class_counts.size),
            "class_distribution": class_counts.to_dict(),
            "min_class_size": int(class_counts.min()),
            "max_class_size": int(class_counts.max()),
        }
    )
    return clean.reset_index(drop=True), report


def build_eda_summary(dataset_path: str | Path) -> tuple[pd.DataFrame, dict[str, Any], pd.DataFrame]:
    """Siapkan data bersih, metadata kualitas, dan statistik panjang chat."""
    clean, report = load_clean_nlu_dataset(dataset_path)
    lengths = clean[TEXT_COLUMN].str.len()
    words = clean[TEXT_COLUMN].str.split().str.len()
    length_by_intent = (
        pd.DataFrame({LABEL_COLUMN: clean[LABEL_COLUMN], "karakter": lengths, "kata": words})
        .groupby(LABEL_COLUMN)
        .agg(jumlah=("kata", "size"), rata_kata=("kata", "mean"), median_kata=("kata", "median"), rata_karakter=("karakter", "mean"))
        .round(2)
        .sort_index()
    )
    report["short_chat_under_3_words"] = int((words < 3).sum())
    report["average_words"] = round(float(words.mean()), 2)
    report["median_words"] = round(float(words.median()), 2)
    return clean, report, length_by_intent


def run_nlu_eda(dataset_path: str | Path, plot: bool = True) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Tampilkan EDA inti dan, bila diminta, distribusi intent dalam grafik."""
    clean, report, length_by_intent = build_eda_summary(dataset_path)

    print("=" * 58)
    print("EDA DATASET NLU HOSTAGE")
    print("=" * 58)
    print(f"Dataset                 : {report['dataset_path']}")
    print(f"Baris mentah / bersih   : {report['rows_raw']} / {report['rows_clean']}")
    print(f"Nilai kosong            : {report['missing_cells_raw']}")
    print(f"Duplikat tepat dihapus  : {report['exact_duplicates_removed']}")
    print(f"Konteks lama dikeluarkan: {report['legacy_context_rows_removed']}")
    print(f"Teks konflik dihapus    : {report['conflicting_texts_removed']}")
    print(f"Jumlah intent           : {report['class_count']}")
    print(f"Ukuran kelas min--maks  : {report['min_class_size']}--{report['max_class_size']}")
    print(f"Rata-rata kata/chat     : {report['average_words']}")
    print(f"Chat < 3 kata           : {report['short_chat_under_3_words']}")
    print("\nDistribusi intent:")
    print(pd.Series(report["class_distribution"], name="jumlah"))
    print("\nStatistik panjang chat per intent:")
    print(length_by_intent)

    if plot:
        try:
            import matplotlib.pyplot as plt

            distribution = pd.Series(report["class_distribution"]).sort_values(ascending=False)
            ax = distribution.plot.bar(figsize=(10, 4), color="#4C78A8", title="Distribusi data per intent")
            ax.set_xlabel("Intent")
            ax.set_ylabel("Jumlah chat")
            plt.xticks(rotation=30, ha="right")
            plt.tight_layout()
            plt.show()
        except ImportError:
            print("[INFO] matplotlib tidak tersedia; EDA tabel tetap lengkap.")

    return clean, report
