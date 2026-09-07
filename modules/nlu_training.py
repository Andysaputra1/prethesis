"""Pipeline training bersama untuk intent classifier game HOSTAGE.

Semua model dilatih dari kolom publik ``teks_chat`` dan ``label_intent``.
Setiap fungsi membuat split stratified yang sama, memilih hyperparameter hanya
di data train, lalu melaporkan macro-F1 pada test set yang tidak disentuh.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np
from sklearn.calibration import CalibratedClassifierCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score, classification_report, f1_score
from sklearn.model_selection import GridSearchCV, StratifiedKFold, train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC

from modules.nlu_eda import LABEL_COLUMN, TEXT_COLUMN, load_clean_nlu_dataset


RANDOM_STATE = 42
DEFAULT_MODEL_FILENAMES = (
    "intent_classifier_svm_tuned.pkl",
    "intent_classifier_svm.pkl",
    "intent_classifier_nb_tuned.pkl",
    "intent_classifier_nb.pkl",
    "intent_classifier.pkl",  # kompatibilitas model notebook lama
)
_TRANSFORMER_INFERENCE_CACHE: dict[tuple[str, str], tuple[Any, Any]] = {}


def _split_dataset(dataset_path: str | Path, test_size: float = 0.2):
    data, data_report = load_clean_nlu_dataset(dataset_path)
    x_train, x_test, y_train, y_test = train_test_split(
        data[TEXT_COLUMN],
        data[LABEL_COLUMN],
        test_size=test_size,
        random_state=RANDOM_STATE,
        stratify=data[LABEL_COLUMN],
    )
    return x_train, x_test, y_train, y_test, data_report


def _cv_folds(y_train, desired_folds: int = 5) -> StratifiedKFold:
    smallest_class = int(y_train.value_counts().min())
    folds = min(desired_folds, smallest_class)
    if folds < 2:
        raise ValueError("Data train tiap intent perlu minimal 2 sampel untuk cross-validation.")
    return StratifiedKFold(n_splits=folds, shuffle=True, random_state=RANDOM_STATE)


def _evaluate(model: Any, x_test, y_test, title: str) -> dict[str, Any]:
    y_pred = model.predict(x_test)
    metrics = {
        "accuracy": round(float(accuracy_score(y_test, y_pred)), 4),
        "f1_macro": round(float(f1_score(y_test, y_pred, average="macro", zero_division=0)), 4),
        "f1_weighted": round(float(f1_score(y_test, y_pred, average="weighted", zero_division=0)), 4),
        "classification_report": classification_report(y_test, y_pred, zero_division=0),
    }
    print(f"\n--- Evaluasi {title} (holdout test set) ---")
    print(f"Accuracy    : {metrics['accuracy']:.4f}")
    print(f"Macro F1    : {metrics['f1_macro']:.4f}")
    print(f"Weighted F1 : {metrics['f1_weighted']:.4f}")
    print(metrics["classification_report"])
    return metrics


def _save_sklearn_model(model: Any, model_dir: str | Path, filename: str) -> Path:
    output_dir = Path(model_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    model_path = output_dir / filename
    joblib.dump(model, model_path)
    print(f"Model tersimpan: {model_path}")
    return model_path


def resolve_model_path(model_dir: str | Path, filename: str | None = None) -> Path:
    """Pilih model eksplisit atau model klasik terbaik yang tersedia."""
    directory = Path(model_dir)
    candidates = (filename,) if filename else DEFAULT_MODEL_FILENAMES
    for candidate in candidates:
        if candidate and (directory / candidate).is_file():
            return directory / candidate
    searched = ", ".join(str(directory / name) for name in candidates if name)
    raise FileNotFoundError(f"Belum ada model sklearn. Jalankan training terlebih dahulu. Dicari: {searched}")


def predict_intent(
    text: str,
    model_dir: str | Path,
    filename: str | None = None,
) -> tuple[str, float]:
    """Prediksi label dan confidence persen dari model sklearn yang tersimpan."""
    model_path = resolve_model_path(model_dir, filename)
    model = joblib.load(model_path)
    predicted = str(model.predict([str(text)])[0])
    if hasattr(model, "predict_proba"):
        confidence = float(np.max(model.predict_proba([str(text)])[0]) * 100)
    elif hasattr(model, "decision_function"):
        scores = np.asarray(model.decision_function([str(text)]), dtype=float).reshape(1, -1)
        probabilities = np.exp(scores - scores.max(axis=1, keepdims=True))
        probabilities /= probabilities.sum(axis=1, keepdims=True)
        confidence = float(probabilities.max() * 100)
    else:
        confidence = float("nan")
    return predicted, round(confidence, 2)


def _result(model: Any, metrics: dict[str, Any], report: dict[str, Any], model_path: Path, **extra: Any) -> dict[str, Any]:
    return {"model": model, "metrics": metrics, "data_report": report, "model_path": str(model_path), **extra}


def _baseline_tfidf() -> TfidfVectorizer:
    return TfidfVectorizer(
        ngram_range=(1, 2),
        min_df=1,
        max_df=0.98,
        sublinear_tf=True,
        strip_accents="unicode",
    )


def _calibration_folds(y_train) -> int:
    """Pilih jumlah fold kalibrasi yang valid untuk kelas terkecil pada train set."""
    folds = min(3, int(y_train.value_counts().min()))
    if folds < 2:
        raise ValueError("Setiap intent pada data train perlu minimal 2 sampel untuk kalibrasi SVM.")
    return folds


def _calibrated_linear_svm(
    c: float,
    class_weight: str | None = "balanced",
    calibration_cv: int = 3,
) -> CalibratedClassifierCV:
    """Linear SVM dengan probabilitas terkalibrasi tanpa SVC(probability=True)."""
    base_svm = LinearSVC(C=c, class_weight=class_weight, random_state=RANDOM_STATE)
    return CalibratedClassifierCV(estimator=base_svm, method="sigmoid", cv=calibration_cv)


def train_svm(
    dataset_path: str | Path,
    model_dir: str | Path,
    filename: str = "intent_classifier_svm.pkl",
) -> dict[str, Any]:
    """Latih baseline TF-IDF + calibrated linear SVM."""
    x_train, x_test, y_train, y_test, report = _split_dataset(dataset_path)
    print(f"SVM | train={len(x_train)} | test={len(x_test)} | kelas={report['class_count']}")
    model = Pipeline([
        ("tfidf", _baseline_tfidf()),
        ("svm", _calibrated_linear_svm(c=2.0, calibration_cv=_calibration_folds(y_train))),
    ])
    model.fit(x_train, y_train)
    metrics = _evaluate(model, x_test, y_test, "SVM baseline")
    model_path = _save_sklearn_model(model, model_dir, filename)
    return _result(model, metrics, report, model_path)


def train_svm_tuned(
    dataset_path: str | Path,
    model_dir: str | Path,
    filename: str = "intent_classifier_svm_tuned.pkl",
    cv_folds: int = 5,
) -> dict[str, Any]:
    """Tuning SVM pada train set, lalu kalibrasi ulang kandidat terbaik.

    Grid Search hanya memakai train set. Test set dipakai sekali di akhir,
    sehingga macro-F1 yang dilaporkan tidak bocor ke proses tuning.
    """
    x_train, x_test, y_train, y_test, report = _split_dataset(dataset_path)
    cv = _cv_folds(y_train, cv_folds)
    search_pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(strip_accents="unicode")),
        ("svm", LinearSVC(random_state=RANDOM_STATE)),
    ])
    # Word n-grams menangkap frasa game, sementara char_wb menguji ketahanan
    # terhadap typo/variasi slang Indonesia. Parameter n-gram dibedakan agar
    # char analyzer tidak keliru memakai rentang (1, 2) milik word analyzer.
    param_grid = [
        {
            "tfidf__analyzer": ["word"],
            "tfidf__ngram_range": [(1, 1), (1, 2), (1, 3)],
            "tfidf__min_df": [1, 2],
            "tfidf__max_df": [0.95, 1.0],
            "tfidf__sublinear_tf": [True],
            "svm__C": [0.25, 0.5, 1.0, 2.0, 4.0, 8.0],
            "svm__class_weight": [None, "balanced"],
        },
        {
            "tfidf__analyzer": ["char_wb"],
            "tfidf__ngram_range": [(3, 5), (3, 6)],
            "tfidf__min_df": [1, 2],
            "tfidf__max_df": [0.95, 1.0],
            "tfidf__sublinear_tf": [True],
            "svm__C": [0.25, 0.5, 1.0, 2.0, 4.0, 8.0],
            "svm__class_weight": [None, "balanced"],
        },
    ]
    print("Memulai SVM Grid Search pada train set...")
    search = GridSearchCV(
        search_pipeline,
        param_grid,
        scoring="f1_macro",
        cv=cv,
        n_jobs=-1,
        refit=True,
        verbose=1,
    )
    search.fit(x_train, y_train)
    best = search.best_params_
    print(f"Parameter SVM terbaik: {best}")
    print(f"Macro-F1 CV terbaik: {search.best_score_:.4f}")

    tuned_tfidf = TfidfVectorizer(
        analyzer=best["tfidf__analyzer"],
        ngram_range=best["tfidf__ngram_range"],
        min_df=best["tfidf__min_df"],
        max_df=best["tfidf__max_df"],
        sublinear_tf=best["tfidf__sublinear_tf"],
        strip_accents="unicode",
    )
    model = Pipeline([
        ("tfidf", tuned_tfidf),
        (
            "svm",
            _calibrated_linear_svm(
                best["svm__C"],
                best["svm__class_weight"],
                calibration_cv=_calibration_folds(y_train),
            ),
        ),
    ])
    model.fit(x_train, y_train)
    metrics = _evaluate(model, x_test, y_test, "SVM tuned")
    model_path = _save_sklearn_model(model, model_dir, filename)
    return _result(model, metrics, report, model_path, best_params=best, cv_f1_macro=round(float(search.best_score_), 4))


def train_naive_bayes(
    dataset_path: str | Path,
    model_dir: str | Path,
    filename: str = "intent_classifier_nb.pkl",
) -> dict[str, Any]:
    """Latih baseline TF-IDF + Multinomial Naive Bayes."""
    x_train, x_test, y_train, y_test, report = _split_dataset(dataset_path)
    print(f"Naive Bayes | train={len(x_train)} | test={len(x_test)} | kelas={report['class_count']}")
    model = Pipeline([
        ("tfidf", _baseline_tfidf()),
        ("nb", MultinomialNB(alpha=0.5)),
    ])
    model.fit(x_train, y_train)
    metrics = _evaluate(model, x_test, y_test, "Naive Bayes baseline")
    model_path = _save_sklearn_model(model, model_dir, filename)
    return _result(model, metrics, report, model_path)


def train_naive_bayes_tuned(
    dataset_path: str | Path,
    model_dir: str | Path,
    filename: str = "intent_classifier_nb_tuned.pkl",
    cv_folds: int = 5,
) -> dict[str, Any]:
    """Tuning Naive Bayes yang mandiri dan bebas dependensi sel notebook.

    Ini menggantikan NB tuning lama yang memakai ``X_train``/``y_train`` dari
    state sel sebelumnya. Fungsi ini sendiri yang membersihkan, membagi, CV,
    mengevaluasi, dan menyimpan model terpilih.
    """
    x_train, x_test, y_train, y_test, report = _split_dataset(dataset_path)
    cv = _cv_folds(y_train, cv_folds)
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(strip_accents="unicode")),
        ("nb", MultinomialNB()),
    ])
    param_grid = {
        "tfidf__ngram_range": [(1, 1), (1, 2)],
        "tfidf__min_df": [1, 2],
        "tfidf__max_df": [0.95, 1.0],
        "tfidf__sublinear_tf": [True],
        "tfidf__use_idf": [True, False],
        "nb__alpha": [0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.0],
        "nb__fit_prior": [True, False],
    }
    print("Memulai Naive Bayes Grid Search pada train set...")
    search = GridSearchCV(
        pipeline,
        param_grid,
        scoring="f1_macro",
        cv=cv,
        n_jobs=-1,
        refit=True,
        verbose=1,
    )
    search.fit(x_train, y_train)
    print(f"Parameter NB terbaik: {search.best_params_}")
    print(f"Macro-F1 CV terbaik: {search.best_score_:.4f}")
    model = search.best_estimator_
    metrics = _evaluate(model, x_test, y_test, "Naive Bayes tuned")
    model_path = _save_sklearn_model(model, model_dir, filename)
    return _result(
        model,
        metrics,
        report,
        model_path,
        best_params=search.best_params_,
        cv_f1_macro=round(float(search.best_score_), 4),
    )


def train_transformer(
    dataset_path: str | Path,
    model_dir: str | Path,
    model_name: str = "indobenchmark/indobert-base-p1",
    epochs: int = 4,
    max_length: int = 128,
    learning_rate: float = 2e-5,
    device: str = "cuda",
) -> dict[str, Any]:
    """Fine-tune IndoBERT secara reproducible untuk klasifikasi intent GPU.

    Dependensi Transformer diimpor saat fungsi dipanggil agar SVM/NB tetap
    dapat dipakai pada environment tanpa PyTorch atau Hugging Face. Transformer
    default memakai CUDA; SVM dan Naive Bayes tetap CPU lewat scikit-learn.
    """
    try:
        import torch
        from datasets import Dataset
        from transformers import AutoModelForSequenceClassification, AutoTokenizer, Trainer, TrainingArguments, set_seed
    except ImportError as error:
        raise ImportError("Transformer butuh torch, datasets, dan transformers.") from error

    from sklearn.preprocessing import LabelEncoder

    device = str(device).strip().lower()
    if device not in {"cpu", "cuda"}:
        raise ValueError("device harus 'cpu' atau 'cuda'.")
    if device == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("device='cuda' dipilih, tetapi CUDA tidak tersedia.")

    x_train, x_test, y_train, y_test, report = _split_dataset(dataset_path)
    encoder = LabelEncoder()
    y_train_encoded = encoder.fit_transform(y_train)
    y_test_encoded = encoder.transform(y_test)
    labels = list(encoder.classes_)
    set_seed(RANDOM_STATE)

    train_frame = {TEXT_COLUMN: x_train.tolist(), "labels": y_train_encoded.tolist()}
    test_frame = {TEXT_COLUMN: x_test.tolist(), "labels": y_test_encoded.tolist()}
    train_dataset = Dataset.from_dict(train_frame)
    test_dataset = Dataset.from_dict(test_frame)
    # Model dasar sudah dipersiapkan di cache lokal. Memakai cache langsung
    # menghindari retry jaringan ketika Hugging Face tidak dapat diakses.
    tokenizer = AutoTokenizer.from_pretrained(model_name, local_files_only=True)

    def tokenize(examples):
        return tokenizer(examples[TEXT_COLUMN], truncation=True, max_length=max_length)

    train_dataset = train_dataset.map(tokenize, batched=True, remove_columns=[TEXT_COLUMN])
    test_dataset = test_dataset.map(tokenize, batched=True, remove_columns=[TEXT_COLUMN])
    id2label = {index: label for index, label in enumerate(labels)}
    label2id = {label: index for index, label in id2label.items()}
    model = AutoModelForSequenceClassification.from_pretrained(
        model_name,
        num_labels=len(labels),
        id2label=id2label,
        label2id=label2id,
        local_files_only=True,
    )

    output_dir = Path(model_dir) / "transformer_results"
    output_dir.mkdir(parents=True, exist_ok=True)

    def compute_metrics(eval_prediction):
        logits, actual = eval_prediction
        predicted = np.argmax(logits, axis=-1)
        return {
            "accuracy": accuracy_score(actual, predicted),
            "f1_macro": f1_score(actual, predicted, average="macro", zero_division=0),
            "f1_weighted": f1_score(actual, predicted, average="weighted", zero_division=0),
        }

    training_args = TrainingArguments(
        output_dir=str(output_dir),
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="f1_macro",
        greater_is_better=True,
        learning_rate=learning_rate,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=32,
        num_train_epochs=epochs,
        weight_decay=0.01,
        warmup_ratio=0.1,
        logging_strategy="epoch",
        save_total_limit=1,
        report_to="none",
        seed=RANDOM_STATE,
        data_seed=RANDOM_STATE,
        dataloader_num_workers=0,
        use_cpu=device == "cpu",
        fp16=device == "cuda",
    )
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=test_dataset,
        tokenizer=tokenizer,
        compute_metrics=compute_metrics,
    )
    print(
        f"Transformer {model_name} | device={device.upper()} | "
        f"train={len(x_train)} | test={len(x_test)} | epoch={epochs}"
    )
    trainer.train()
    prediction_output = trainer.predict(test_dataset)
    y_pred = np.argmax(prediction_output.predictions, axis=-1)
    metrics = {
        "accuracy": round(float(accuracy_score(y_test_encoded, y_pred)), 4),
        "f1_macro": round(float(f1_score(y_test_encoded, y_pred, average="macro", zero_division=0)), 4),
        "f1_weighted": round(float(f1_score(y_test_encoded, y_pred, average="weighted", zero_division=0)), 4),
        "classification_report": classification_report(y_test_encoded, y_pred, target_names=labels, zero_division=0),
    }
    print("\n--- Evaluasi Transformer (holdout test set) ---")
    print(f"Accuracy    : {metrics['accuracy']:.4f}")
    print(f"Macro F1    : {metrics['f1_macro']:.4f}")
    print(f"Weighted F1 : {metrics['f1_weighted']:.4f}")
    print(metrics["classification_report"])

    final_dir = Path(model_dir) / "intent_classifier_transformer"
    trainer.save_model(str(final_dir))
    tokenizer.save_pretrained(str(final_dir))
    joblib.dump(encoder, final_dir / "label_encoder.pkl")
    (final_dir / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(f"Model Transformer tersimpan: {final_dir}")
    return _result(model, metrics, report, final_dir, tokenizer=tokenizer, label_encoder=encoder)


def predict_transformer_intent(
    text: str,
    model_dir: str | Path,
    device: str = "cuda",
) -> tuple[str, float]:
    """Prediksi satu chat dengan Transformer hasil fine-tuning.

    Fungsi ini dipisahkan dari training agar sel uji notebook dapat menguji
    chat baru pada model Transformer dengan format yang sama seperti model
    klasik: ``(label_intent, confidence_persen)``.
    """
    try:
        import torch
        from transformers import AutoModelForSequenceClassification, AutoTokenizer
    except ImportError as error:
        raise ImportError("Prediksi Transformer butuh torch dan transformers.") from error

    requested_device = str(device).strip().lower()
    if requested_device not in {"cpu", "cuda"}:
        raise ValueError("device harus 'cpu' atau 'cuda'.")
    if requested_device == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("device='cuda' dipilih, tetapi CUDA tidak tersedia.")

    saved_model_dir = Path(model_dir) / "intent_classifier_transformer"
    if not saved_model_dir.is_dir():
        raise FileNotFoundError(
            "Model Transformer belum tersedia. Jalankan train_transformer_model() terlebih dahulu: "
            f"{saved_model_dir}"
        )

    cache_key = (str(saved_model_dir.resolve()), requested_device)
    if cache_key not in _TRANSFORMER_INFERENCE_CACHE:
        runtime_device = torch.device(requested_device)
        tokenizer = AutoTokenizer.from_pretrained(saved_model_dir)
        model = AutoModelForSequenceClassification.from_pretrained(saved_model_dir)
        model.to(runtime_device)
        model.eval()
        _TRANSFORMER_INFERENCE_CACHE[cache_key] = (tokenizer, model)
    tokenizer, model = _TRANSFORMER_INFERENCE_CACHE[cache_key]
    runtime_device = next(model.parameters()).device
    encoded = tokenizer(str(text), return_tensors="pt", truncation=True, max_length=128)
    encoded = {name: value.to(runtime_device) for name, value in encoded.items()}
    with torch.no_grad():
        probabilities = torch.softmax(model(**encoded).logits, dim=-1)[0]
    label_index = int(torch.argmax(probabilities).item())
    labels = model.config.id2label
    label = labels.get(label_index, labels.get(str(label_index), str(label_index)))
    confidence = round(float(probabilities[label_index].item() * 100), 2)
    return str(label), confidence


HOSTAGE_BENCHMARK_TESTS = (
    ("accusing", "B kena Gag Order ketika mulai ditanya alibinya, menurutku itu pola Hitman."),
    ("defending", "Aku bukan Hitman. Tuduhan itu tidak punya bukti dari chat publik."),
    ("bluffing", "Aku Spy dan semalam Guard Raka, jadi jangan curigai dia."),
    ("probing", "Stalker, kamu Peek siapa semalam dan apa hasil yang kamu lihat?"),
    ("deflecting", "Jangan hanya fokus ke aku; cek D yang ceritanya berubah setiap ditanya."),
    ("persuading", "Vote C saja, dia paling diuntungkan ketika seseorang mendadak diam."),
    ("claiming", "Klaimku Civilian, jadi aku memang tidak memiliki aksi malam."),
    ("neutral", "Malam ini chat terkunci, kita lanjut diskusi setelah fase pagi."),
    ("accusing", "A selalu menghindar saat kita tanya kenapa dia menuduh tanpa bukti."),
    ("defending", "Diamku bukan pengakuan; aku masih bisa menjelaskan alibiku di fase siang."),
)


def run_all_nlu_models(
    dataset_path: str | Path,
    model_dir: str | Path,
    *,
    run_transformer: bool = True,
    run_tuning: bool = True,
    transformer_epochs: int = 4,
    transformer_device: str = "cuda",
) -> tuple[dict[str, Any], Any, Any]:
    """Latih seluruh classifier dan bandingkan holdout serta 10 chat game.

    Mengembalikan ``(artifacts, hasil_holdout, hasil_10_chat)``. Split untuk
    setiap model deterministik (random state sama), sehingga perbandingan
    holdout tidak bercampur dengan data training/tuning.
    """
    import time

    import pandas as pd

    model_dir = Path(model_dir)
    model_runs: list[tuple[str, Any, str | None, str]] = [
        ("SVM baseline", lambda: train_svm(dataset_path, model_dir), "intent_classifier_svm.pkl", "sklearn"),
        ("Naive Bayes baseline", lambda: train_naive_bayes(dataset_path, model_dir), "intent_classifier_nb.pkl", "sklearn"),
    ]
    if run_tuning:
        model_runs.extend(
            [
                ("SVM tuned", lambda: train_svm_tuned(dataset_path, model_dir), "intent_classifier_svm_tuned.pkl", "sklearn"),
                ("Naive Bayes tuned", lambda: train_naive_bayes_tuned(dataset_path, model_dir), "intent_classifier_nb_tuned.pkl", "sklearn"),
            ]
        )
    if run_transformer:
        model_runs.append(
            (
                "IndoBERT Transformer",
                lambda: train_transformer(
                    dataset_path,
                    model_dir,
                    epochs=transformer_epochs,
                    device=transformer_device,
                ),
                None,
                "transformer",
            )
        )

    artifacts: dict[str, Any] = {}
    training_rows: list[dict[str, Any]] = []
    for model_name, trainer, filename, model_kind in model_runs:
        print(f"\n{'=' * 72}\nMENJALANKAN: {model_name}\n{'=' * 72}")
        started = time.perf_counter()
        try:
            artifact = trainer()
            artifacts[model_name] = {"filename": filename, "kind": model_kind, "artifact": artifact}
            metrics = artifact["metrics"]
            training_rows.append(
                {
                    "model": model_name,
                    "accuracy_holdout": metrics["accuracy"],
                    "macro_f1_holdout": metrics["f1_macro"],
                    "weighted_f1_holdout": metrics["f1_weighted"],
                    "waktu_detik": round(time.perf_counter() - started, 1),
                    "status": "berhasil",
                }
            )
        except Exception as error:
            training_rows.append(
                {
                    "model": model_name,
                    "waktu_detik": round(time.perf_counter() - started, 1),
                    "status": f"gagal: {error}",
                }
            )
            print(f"[GAGAL] {model_name}: {error}")

    training_summary = pd.DataFrame(training_rows)
    if "macro_f1_holdout" in training_summary:
        training_summary = training_summary.sort_values("macro_f1_holdout", ascending=False, na_position="last")

    manual_rows: list[dict[str, Any]] = []
    for model_name, saved in artifacts.items():
        correct = 0
        print(f"\n--- 10 chat uji: {model_name} ---")
        for expected, chat in HOSTAGE_BENCHMARK_TESTS:
            if saved["kind"] == "transformer":
                predicted, confidence = predict_transformer_intent(chat, model_dir, device=transformer_device)
            else:
                predicted, confidence = predict_intent(chat, model_dir, filename=saved["filename"])
            is_correct = predicted == expected
            correct += is_correct
            print(
                f"expected={expected:12} | predicted={predicted:12} | "
                f"confidence={confidence:6.2f}% | {'OK' if is_correct else 'MISS'}"
            )
        manual_rows.append(
            {
                "model": model_name,
                "benar_dari_10": correct,
                "akurasi_10_chat": round(correct / len(HOSTAGE_BENCHMARK_TESTS), 2),
            }
        )

    manual_summary = pd.DataFrame(manual_rows).sort_values("benar_dari_10", ascending=False)
    return artifacts, training_summary.reset_index(drop=True), manual_summary.reset_index(drop=True)
