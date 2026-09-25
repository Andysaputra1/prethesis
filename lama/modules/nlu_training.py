"""Pipeline training bersama untuk intent classifier game HOSTAGE.

Semua model dilatih dari kolom publik ``teks_chat`` dan ``label_intent``.
Setiap fungsi membuat split stratified yang sama, memilih hyperparameter hanya
di data train, lalu melaporkan macro-F1 pada test set yang tidak disentuh.

Alur baca: split data -> helper evaluasi -> baseline/Grid Search -> Optuna
-> IndoBERT -> runner perbandingan. Fungsi publik menerima path dataset dan
folder model sehingga tidak bergantung pada variabel notebook.
Grid Search mencoba seluruh kombinasi; Optuna mencoba konfigurasi melalui TPE.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np
from sklearn.calibration import CalibratedClassifierCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
)
from sklearn.model_selection import (
    GridSearchCV,
    StratifiedKFold,
    cross_val_score,
    train_test_split,
)
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC

from lama.modules.nlu_eda import LABEL_COLUMN, TEXT_COLUMN, load_clean_nlu_dataset


RANDOM_STATE = 42
DEFAULT_MODEL_FILENAMES = (
    "intent_classifier_svm_tuned.pkl",
    "intent_classifier_svm.pkl",
    "intent_classifier_nb_tuned.pkl",
    "intent_classifier_nb.pkl",
    "intent_classifier.pkl",  # kompatibilitas model notebook lama
)
_TRANSFORMER_INFERENCE_CACHE: dict[tuple[str, str], tuple[Any, Any]] = {}


# -----------------------------------------------------------------------------
# Data: cleaning bersama dan split deterministik untuk semua model.
# -----------------------------------------------------------------------------

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


def _split_transformer_dataset(dataset_path: str | Path, validation_size: float = 0.15):
    """Pertahankan test 20% yang sama dengan SVM/NB; ambil validation dari train.

    validation_size adalah proporsi terhadap seluruh data (default 65/15/20).
    Indeks data bersih dipertahankan agar pemisahan dapat diaudit.
    """
    if not 0 < validation_size < 0.8:
        raise ValueError("validation_size harus di antara 0 dan 0.8.")
    x_pool, x_test, y_pool, y_test, report = _split_dataset(dataset_path)
    try:
        x_train, x_val, y_train, y_val = train_test_split(
            x_pool, y_pool, test_size=validation_size / 0.8,
            random_state=RANDOM_STATE, stratify=y_pool,
        )
    except ValueError as error:
        raise ValueError("Data per intent tidak cukup untuk split train/validation/test stratified.") from error
    if set(y_train) != set(y_pool) or set(y_val) != set(y_pool):
        raise ValueError("Setiap intent harus tersedia pada train dan validation; tambah data per intent.")
    return x_train, x_val, x_test, y_train, y_val, y_test, report


# -----------------------------------------------------------------------------
# Evaluasi, penyimpanan artefak, dan prediksi model klasik.
# -----------------------------------------------------------------------------

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
    """Pilih nama eksplisit atau prioritas file lama; bukan ranking metrik.

    Untuk model Optuna, berikan filename agar varian yang dipakai jelas.
    """
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


def _result(
    model: Any,
    metrics: dict[str, Any],
    report: dict[str, Any],
    model_path: Path,
    **extra: Any,
) -> dict[str, Any]:
    """Samakan format hasil agar notebook dapat membandingkan semua model."""
    return {
        "model": model,
        "metrics": metrics,
        "data_report": report,
        "model_path": str(model_path),
        **extra,
    }


# -----------------------------------------------------------------------------
# Model klasik: baseline dan Grid Search (parameter lama dipertahankan).
# -----------------------------------------------------------------------------

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
            "tfidf__sublinear_tf": [True, False],
            "svm__C": [0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 4.0, 8.0],
            "svm__class_weight": [None, "balanced"],
        },
        {
            "tfidf__analyzer": ["char_wb"],
            "tfidf__ngram_range": [(3, 5), (3, 6)],
            "tfidf__min_df": [1, 2],
            "tfidf__max_df": [0.95, 1.0],
            "tfidf__sublinear_tf": [True, False],
            "svm__C": [0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 4.0, 8.0],
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
        "tfidf__sublinear_tf": [True, False],
        "tfidf__use_idf": [True, False],
        "tfidf__norm": ["l2", "l1", None],
        "nb__alpha": [0.01, 0.05, 0.075, 0.1, 0.15, 0.2, 0.25, 0.5, 1.0, 2.0],
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


# -----------------------------------------------------------------------------
# Tuning Optuna: sampling -> CV pada train -> refit -> evaluasi test -> simpan.
# -----------------------------------------------------------------------------

def _suggest_optuna_params(trial: Any, model_kind: str) -> dict[str, Any]:
    """Usulkan fitur dan classifier; rentang lama tetap tercakup di Optuna."""
    analyzer = (
        trial.suggest_categorical("analyzer", ["word", "char_wb"])
        if model_kind == "svm" else "word"
    )
    # Nama parameter dipisah agar pilihan kategorikal tidak berubah antar-trial.
    if analyzer == "word":
        upper = trial.suggest_categorical(
            "word_ngram_max", [1, 2, 3] if model_kind == "svm" else [1, 2]
        )
        ngram_range = (1, upper)
    else:
        upper = trial.suggest_categorical("char_ngram_max", [5, 6])
        ngram_range = (3, upper)

    params = {
        "tfidf__analyzer": analyzer,
        "tfidf__ngram_range": ngram_range,
        "tfidf__min_df": trial.suggest_categorical("min_df", [1, 2]),
        "tfidf__max_df": trial.suggest_categorical("max_df", [0.95, 1.0]),
        "tfidf__sublinear_tf": trial.suggest_categorical("sublinear_tf", [True, False]),
    }
    if model_kind == "svm":
        params.update({
            "svm__C": trial.suggest_float("C", 0.25, 8.0, log=True),
            "svm__class_weight": trial.suggest_categorical(
                "class_weight", [None, "balanced"]
            ),
        })
    else:
        params.update({
            "tfidf__use_idf": trial.suggest_categorical("use_idf", [True, False]),
            "tfidf__norm": trial.suggest_categorical("norm", ["l2", "l1", None]),
            "nb__alpha": trial.suggest_float("alpha", 0.01, 2.0, log=True),
            "nb__fit_prior": trial.suggest_categorical("fit_prior", [True, False]),
        })
    return params


def _build_optuna_model(
    model_kind: str, params: dict[str, Any], calibration_folds: int = 3,
) -> Any:
    """Bangun estimator yang sama untuk CV dan refit akhir."""
    classifier = (
        LinearSVC(random_state=RANDOM_STATE, max_iter=10000)
        if model_kind == "svm" else MultinomialNB()
    )
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(strip_accents="unicode")),
        (model_kind, classifier),
    ])
    pipeline.set_params(**params)
    if model_kind == "svm":
        # Kalibrator membungkus seluruh pipeline: TF-IDF ikut fit hanya pada
        # train fold internal. Fold kalibrasi tidak membentuk vocabulary/IDF.
        return CalibratedClassifierCV(
            estimator=pipeline,
            method="sigmoid",
            cv=StratifiedKFold(
                n_splits=calibration_folds, shuffle=True, random_state=RANDOM_STATE,
            ),
            n_jobs=1,
        )
    return pipeline


def _train_classical_optuna(
    dataset_path: str | Path,
    model_dir: str | Path,
    filename: str,
    *,
    model_kind: str,
    n_trials: int,
    cv_folds: int,
    timeout: float | None,
    n_jobs: int,
) -> dict[str, Any]:
    """Alur bersama Optuna; test tidak pernah dipakai oleh objective."""
    import math
    import tempfile

    try:
        import optuna
    except ImportError as error:
        raise ImportError("Tuning Optuna memerlukan paket optuna: pip install optuna") from error

    if isinstance(n_trials, bool) or not isinstance(n_trials, int) or n_trials < 1:
        raise ValueError("n_trials harus bilangan bulat positif.")
    if isinstance(cv_folds, bool) or not isinstance(cv_folds, int) or cv_folds < 2:
        raise ValueError("cv_folds harus bilangan bulat minimal 2.")
    if timeout is not None and (not math.isfinite(timeout) or timeout <= 0):
        raise ValueError("timeout harus positif atau None.")
    if isinstance(n_jobs, bool) or not isinstance(n_jobs, int) or n_jobs == 0:
        raise ValueError("n_jobs harus bilangan bulat selain 0.")

    # 1. Gunakan split test yang sama dengan baseline dan Grid Search.
    x_train, x_test, y_train, y_test, report = _split_dataset(dataset_path)
    cv = _cv_folds(y_train, cv_folds)
    folds = list(cv.split(x_train, y_train))
    calibration_folds = 3
    if model_kind == "svm":
        smallest_inner_class = min(
            int(y_train.iloc[train_idx].value_counts().min())
            for train_idx, _ in folds
        )
        calibration_folds = min(3, smallest_inner_class)
        if calibration_folds < 2:
            raise ValueError("Data train per kelas tidak cukup untuk CV dan kalibrasi SVM.")

    # Setiap pemanggilan memiliki direktori sendiri agar riwayat tidak tertimpa.
    output_root = Path(model_dir) / "optuna_results"
    output_root.mkdir(parents=True, exist_ok=True)
    run_dir = Path(tempfile.mkdtemp(prefix=f"{model_kind}_", dir=output_root))
    study = optuna.create_study(
        direction="maximize",
        sampler=optuna.samplers.TPESampler(seed=RANDOM_STATE),
        pruner=optuna.pruners.NopPruner(),
        study_name=f"{model_kind}_macro_f1",
    )

    # 2. Tiap trial dievaluasi pada fold yang identik. Seluruh preprocessing
    # berada di estimator. Simpan skor tiap fold untuk menilai variasi hasil.
    def objective(trial):
        params = _suggest_optuna_params(trial, model_kind)
        estimator = _build_optuna_model(model_kind, params, calibration_folds)
        scores = cross_val_score(
            estimator, x_train, y_train, cv=folds,
            scoring="f1_macro", n_jobs=n_jobs, error_score="raise",
        )
        trial.set_user_attr("pipeline_params", params)
        trial.set_user_attr("fold_scores", scores.tolist())
        trial.set_user_attr("cv_std", float(scores.std()))
        return float(scores.mean())

    def save_trials(study, trial):
        study.trials_dataframe().to_csv(run_dir / "trials.csv", index=False)

    print(f"Optuna {model_kind.upper()}: {n_trials} trial, {len(folds)} fold, macro-F1.")
    # Trial berurutan menjaga urutan sampling TPE; hanya fold CV diparalelkan.
    study.optimize(
        objective, n_trials=n_trials, timeout=timeout,
        n_jobs=1, callbacks=[save_trials],
    )
    best = dict(study.best_trial.user_attrs["pipeline_params"])
    best["tfidf__ngram_range"] = tuple(best["tfidf__ngram_range"])
    print("Parameter Optuna terbaik:", best)
    print(f"Macro-F1 CV terbaik: {study.best_value:.4f}")

    # 3. Latih konfigurasi terpilih pada train, lalu evaluasi test satu kali.
    model = _build_optuna_model(model_kind, best, calibration_folds)
    model.fit(x_train, y_train)
    metrics = _evaluate(model, x_test, y_test, f"{model_kind.upper()} Optuna")
    model_path = _save_sklearn_model(model, model_dir, filename)

    # 4. Catat hasil dan indeks split untuk pelaporan serta audit eksperimen.
    summary = {
        "method": "Optuna TPE", "model_kind": model_kind,
        "optuna_version": optuna.__version__, "seed": RANDOM_STATE,
        "n_trials_requested": n_trials, "n_trials_completed": len(study.trials),
        "cv_folds": len(folds), "timeout": timeout, "cv_n_jobs": n_jobs,
        "calibration_folds": calibration_folds if model_kind == "svm" else None,
        "selection_metric": "cv_f1_macro", "test_used_for_selection": False,
        "best_trial": study.best_trial.number, "best_params": best,
        "cv_f1_macro": study.best_value,
        "cv_std": study.best_trial.user_attrs["cv_std"],
        "metrics": metrics, "data_report": report, "model_path": str(model_path),
    }
    (run_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8",
    )
    split_indices = {
        "train": x_train.index.tolist(), "test": x_test.index.tolist(),
        "cv": [
            {"train": x_train.iloc[a].index.tolist(), "validation": x_train.iloc[b].index.tolist()}
            for a, b in folds
        ],
    }
    (run_dir / "split_indices.json").write_text(
        json.dumps(split_indices, indent=2), encoding="utf-8",
    )
    return _result(
        model, metrics, report, model_path, best_params=best,
        cv_f1_macro=round(float(study.best_value), 4),
        cv_std=float(study.best_trial.user_attrs["cv_std"]),
        study=study, run_dir=str(run_dir), training_summary=summary,
    )


def train_naive_bayes_optuna(
    dataset_path: str | Path,
    model_dir: str | Path,
    filename: str = "intent_classifier_nb_optuna.pkl",
    *,
    n_trials: int = 50,
    cv_folds: int = 5,
    timeout: float | None = None,
    n_jobs: int = -1,
) -> dict[str, Any]:
    """Tuning TF-IDF + MultinomialNB memakai TPE dan macro-F1 CV.

    n_trials membatasi jumlah konfigurasi; timeout membatasi waktu pencarian
    dalam detik (trial yang berjalan diselesaikan). n_jobs mengatur paralel CV.
    Model, ringkasan JSON, dan trials.csv disimpan terpisah dari Grid Search.
    """
    return _train_classical_optuna(
        dataset_path, model_dir, filename, model_kind="nb",
        n_trials=n_trials, cv_folds=cv_folds, timeout=timeout, n_jobs=n_jobs,
    )


def train_svm_optuna(
    dataset_path: str | Path,
    model_dir: str | Path,
    filename: str = "intent_classifier_svm_optuna.pkl",
    *,
    n_trials: int = 50,
    cv_folds: int = 5,
    timeout: float | None = None,
    n_jobs: int = -1,
) -> dict[str, Any]:
    """Tuning SVM terkalibrasi memakai TPE dan macro-F1 CV.

    Setiap fold luar memuat kalibrasi internal atas pipeline TF-IDF + SVM.
    Skor CV dan model akhir memakai struktur yang sama. Karena kalibrasi
    bertingkat, satu trial SVM membutuhkan lebih banyak fit daripada NB.
    Argumen kendali pencarian sama dengan train_naive_bayes_optuna.
    """
    return _train_classical_optuna(
        dataset_path, model_dir, filename, model_kind="svm",
        n_trials=n_trials, cv_folds=cv_folds, timeout=timeout, n_jobs=n_jobs,
    )


# -----------------------------------------------------------------------------
# IndoBERT: fine-tuning, seleksi validation, dan inferensi.
# -----------------------------------------------------------------------------

def train_transformer(
    dataset_path: str | Path,
    model_dir: str | Path,
    model_name: str = "indobenchmark/indobert-base-p1",
    epochs: int = 12,
    max_length: int = 128,
    learning_rate: float = 2e-5,
    device: str = "cuda",
    *,
    learning_rates: tuple[float, ...] | None = None,
    validation_size: float = 0.15,
    batch_size: int = 8,
    eval_batch_size: int = 16,
    gradient_accumulation_steps: int = 2,
    weight_decay: float = 0.01,
    warmup_ratio: float = 0.1,
    lr_scheduler_type: str = "linear",
    dropout: float = 0.1,
    label_smoothing_factor: float = 0.0,
    max_grad_norm: float = 1.0,
    early_stopping_patience: int = 3,
    early_stopping_threshold: float = 0.001,
    gradient_checkpointing: bool = False,
) -> dict[str, Any]:
    """Full fine-tuning IndoBERT, seleksi validation, lalu satu evaluasi test.

    ``epochs`` adalah batas maksimum; early stopping memantau validation
    macro-F1. ``learning_rates`` mengaktifkan pencarian LR, setiap trial mulai
    dari pretrained dan seed yang sama. Jika None, gunakan ``learning_rate``.
    Test 20% identik dengan model klasik; validation 15% diambil dari pool train.
    Checkpoint dan riwayat setiap run disimpan terpisah untuk audit eksperimen.
    """
    import gc
    import math
    import tempfile

    try:
        import torch
        import transformers
        from datasets import Dataset
        from transformers import (
            AutoModelForSequenceClassification, AutoTokenizer, DataCollatorWithPadding,
            EarlyStoppingCallback, Trainer, TrainingArguments, set_seed,
        )
    except ImportError as error:
        raise ImportError("Transformer butuh torch, datasets, transformers, dan accelerate.") from error

    from sklearn.preprocessing import LabelEncoder

    device = str(device).strip().lower()
    if device not in {"cpu", "cuda"}:
        raise ValueError("device harus 'cpu' atau 'cuda'.")
    if device == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("device='cuda' dipilih, tetapi CUDA tidak tersedia.")
    for name, value in {
        "epochs": epochs, "max_length": max_length, "batch_size": batch_size,
        "eval_batch_size": eval_batch_size,
        "gradient_accumulation_steps": gradient_accumulation_steps,
        "early_stopping_patience": early_stopping_patience,
    }.items():
        if not isinstance(value, int) or isinstance(value, bool) or value < 1:
            raise ValueError(f"{name} harus bilangan bulat positif.")
    rates = list(dict.fromkeys(learning_rates if learning_rates is not None else [learning_rate]))
    if not rates or any(not math.isfinite(rate) or rate <= 0 for rate in rates):
        raise ValueError("learning rate harus positif dan daftar trial tidak boleh kosong.")
    if not 0 <= dropout < 1 or not 0 <= label_smoothing_factor < 1:
        raise ValueError("dropout dan label_smoothing_factor harus di rentang [0, 1).")
    if not 0 <= warmup_ratio <= 1 or not math.isfinite(weight_decay) or weight_decay < 0:
        raise ValueError("warmup_ratio harus di [0, 1] dan weight_decay harus nonnegatif.")
    if not math.isfinite(max_grad_norm) or max_grad_norm <= 0:
        raise ValueError("max_grad_norm harus positif.")
    if not math.isfinite(early_stopping_threshold) or early_stopping_threshold < 0:
        raise ValueError("early_stopping_threshold harus nonnegatif.")

    x_train, x_val, x_test, y_train, y_val, y_test, report = _split_transformer_dataset(
        dataset_path, validation_size,
    )
    encoder = LabelEncoder().fit(y_train)
    labels = encoder.classes_.tolist()
    y_test_encoded = encoder.transform(y_test)
    id2label = dict(enumerate(labels))
    label2id = {label: index for index, label in id2label.items()}
    tokenizer = AutoTokenizer.from_pretrained(model_name, local_files_only=True)
    if max_length > tokenizer.model_max_length:
        raise ValueError(f"max_length melebihi kapasitas tokenizer: {tokenizer.model_max_length}.")

    def make_dataset(texts, actual):
        dataset = Dataset.from_dict({TEXT_COLUMN: texts.tolist(), "labels": encoder.transform(actual).tolist()})
        return dataset.map(
            lambda examples: tokenizer(examples[TEXT_COLUMN], truncation=True, max_length=max_length),
            batched=True, remove_columns=[TEXT_COLUMN],
        )

    train_dataset = make_dataset(x_train, y_train)
    validation_dataset = make_dataset(x_val, y_val)
    collator = DataCollatorWithPadding(tokenizer, pad_to_multiple_of=8 if device == "cuda" else None)
    output_root = Path(model_dir) / "transformer_results"
    output_root.mkdir(parents=True, exist_ok=True)
    output_dir = Path(tempfile.mkdtemp(prefix="run_", dir=output_root)).resolve()
    split_indices = {
        name: texts.index.tolist()
        for name, texts in (("train", x_train), ("validation", x_val), ("test", x_test))
    }
    (output_dir / "split_indices.json").write_text(json.dumps(split_indices, indent=2), encoding="utf-8")

    def compute_metrics(eval_prediction):
        logits, actual = eval_prediction
        predicted = np.argmax(logits, axis=-1)
        return {
            "accuracy": accuracy_score(actual, predicted),
            "f1_macro": f1_score(actual, predicted, average="macro", zero_division=0),
            "f1_weighted": f1_score(actual, predicted, average="weighted", zero_division=0),
        }

    trial_results = []
    for trial_index, rate in enumerate(rates, start=1):
        set_seed(RANDOM_STATE)
        model = AutoModelForSequenceClassification.from_pretrained(
            model_name, num_labels=len(labels), id2label=id2label, label2id=label2id,
            hidden_dropout_prob=dropout, attention_probs_dropout_prob=dropout,
            classifier_dropout=dropout, local_files_only=True,
        )
        if max_length > model.config.max_position_embeddings:
            raise ValueError("max_length melebihi max_position_embeddings model.")
        model.config.nlu_max_length = max_length
        training_args = TrainingArguments(
            output_dir=str(output_dir / f"trial_{trial_index}"),
            eval_strategy="epoch", save_strategy="epoch", logging_strategy="epoch",
            load_best_model_at_end=True, metric_for_best_model="f1_macro", greater_is_better=True,
            learning_rate=rate, per_device_train_batch_size=batch_size,
            per_device_eval_batch_size=eval_batch_size,
            gradient_accumulation_steps=gradient_accumulation_steps,
            num_train_epochs=epochs, weight_decay=weight_decay, warmup_ratio=warmup_ratio,
            lr_scheduler_type=lr_scheduler_type, label_smoothing_factor=label_smoothing_factor,
            max_grad_norm=max_grad_norm, gradient_checkpointing=gradient_checkpointing,
            save_total_limit=1, save_only_model=True, report_to="none",
            disable_tqdm=True,
            seed=RANDOM_STATE, data_seed=RANDOM_STATE, dataloader_num_workers=0,
            use_cpu=device == "cpu", fp16=device == "cuda",
        )
        trainer = Trainer(
            model=model, args=training_args, train_dataset=train_dataset,
            eval_dataset=validation_dataset, processing_class=tokenizer,
            data_collator=collator, compute_metrics=compute_metrics,
            callbacks=[EarlyStoppingCallback(
                early_stopping_patience=early_stopping_patience,
                early_stopping_threshold=early_stopping_threshold,
            )],
        )
        print(
            f"Transformer trial {trial_index}/{len(rates)} | {model_name} | {device.upper()} | "
            f"train={len(x_train)} val={len(x_val)} test={len(x_test)} | "
            f"max_epoch={epochs} lr={rate:g} effective_batch="
            f"{batch_size * gradient_accumulation_steps * training_args.world_size}",
            flush=True,
        )
        trainer.train()
        history = trainer.state.log_history
        eval_history = [row for row in history if "eval_f1_macro" in row]
        best_eval = max(eval_history, key=lambda row: row["eval_f1_macro"])
        trial_result = {
            "trial": trial_index, "learning_rate": rate,
            "best_validation_f1_macro": float(trainer.state.best_metric),
            "best_epoch": float(best_eval["epoch"]),
            "epochs_trained": float(trainer.state.epoch),
            "best_checkpoint": trainer.state.best_model_checkpoint,
            "history": history,
        }
        trial_results.append(trial_result)
        (output_dir / "trials.json").write_text(json.dumps(trial_results, indent=2), encoding="utf-8")
        print(f"Trial {trial_index}: best epoch={best_eval['epoch']}, val macro-F1={trainer.state.best_metric:.4f}", flush=True)
        # Hanya satu model/optimizer di GPU selama pencarian.
        del trainer, model
        gc.collect()
        if device == "cuda":
            torch.cuda.empty_cache()

    best_trial = max(trial_results, key=lambda row: row["best_validation_f1_macro"])
    model = AutoModelForSequenceClassification.from_pretrained(best_trial["best_checkpoint"], local_files_only=True)
    trainer = Trainer(
        model=model,
        args=TrainingArguments(
            output_dir=str(output_dir / "evaluation"), per_device_eval_batch_size=eval_batch_size,
            report_to="none", use_cpu=device == "cpu", dataloader_num_workers=0,
            disable_tqdm=True,
        ),
        processing_class=tokenizer, data_collator=collator,
    )
    # Test baru diprediksi setelah semua trial selesai dan pemenang terkunci.
    prediction_output = trainer.predict(make_dataset(x_test, y_test))
    y_pred = np.argmax(prediction_output.predictions, axis=-1)
    metrics = {
        "accuracy": round(float(accuracy_score(y_test_encoded, y_pred)), 4),
        "f1_macro": round(float(f1_score(y_test_encoded, y_pred, average="macro", zero_division=0)), 4),
        "f1_weighted": round(float(f1_score(y_test_encoded, y_pred, average="weighted", zero_division=0)), 4),
        "classification_report": classification_report(
            y_test_encoded, y_pred, labels=list(id2label), target_names=labels, zero_division=0,
        ),
        "confusion_matrix": confusion_matrix(y_test_encoded, y_pred, labels=list(id2label)).tolist(),
        "labels": labels,
    }
    summary = {
        "model_name": model_name, "seed": RANDOM_STATE,
        "torch_version": torch.__version__, "transformers_version": transformers.__version__,
        "device": device, "max_epochs": epochs, "max_length": max_length,
        "batch_size": batch_size, "eval_batch_size": eval_batch_size,
        "gradient_accumulation_steps": gradient_accumulation_steps,
        "effective_batch_size": batch_size * gradient_accumulation_steps * training_args.world_size,
        "weight_decay": weight_decay, "warmup_ratio": warmup_ratio,
        "lr_scheduler_type": lr_scheduler_type, "dropout": dropout,
        "label_smoothing_factor": label_smoothing_factor, "max_grad_norm": max_grad_norm,
        "gradient_checkpointing": gradient_checkpointing,
        "early_stopping_patience": early_stopping_patience,
        "early_stopping_threshold": early_stopping_threshold,
        "split_sizes": {name: len(indices) for name, indices in split_indices.items()},
        "validation_size": validation_size, "data_report": report,
        "selection_metric": "validation_f1_macro", "test_used_for_selection": False,
        "best_trial": {key: value for key, value in best_trial.items() if key != "history"},
        "trials": trial_results, "run_dir": str(output_dir),
    }
    print("\n--- Evaluasi Transformer (test; seleksi hanya dari validation) ---")
    print(f"Best LR: {best_trial['learning_rate']:g} | best epoch: {best_trial['best_epoch']}")
    print(f"Accuracy: {metrics['accuracy']:.4f} | Macro F1: {metrics['f1_macro']:.4f}")
    print(metrics["classification_report"])

    final_dir = Path(model_dir) / "intent_classifier_transformer"
    trainer.save_model(str(final_dir))
    tokenizer.save_pretrained(str(final_dir))
    joblib.dump(encoder, final_dir / "label_encoder.pkl")
    for name, payload in (("metrics.json", metrics), ("training_summary.json", summary)):
        (final_dir / name).write_text(json.dumps(payload, indent=2), encoding="utf-8")
        (output_dir / name).write_text(json.dumps(payload, indent=2), encoding="utf-8")
    predictions = x_test.to_frame(name=TEXT_COLUMN)
    predictions["actual"] = y_test.to_numpy()
    predictions["predicted"] = encoder.inverse_transform(y_pred)
    predictions.to_csv(final_dir / "test_predictions.csv", index_label="clean_row_index")
    # Notebook dapat melakukan retraining tanpa restart kernel; buang cache model lama.
    for key in list(_TRANSFORMER_INFERENCE_CACHE):
        if key[0] == str(final_dir.resolve()):
            del _TRANSFORMER_INFERENCE_CACHE[key]
    print(f"Model Transformer tersimpan: {final_dir}")
    return _result(
        model, metrics, report, final_dir, tokenizer=tokenizer,
        label_encoder=encoder, training_summary=summary,
    )


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
    encoded = tokenizer(
        str(text), return_tensors="pt", truncation=True,
        max_length=getattr(model.config, "nlu_max_length", 128),
    )
    encoded = {name: value.to(runtime_device) for name, value in encoded.items()}
    with torch.no_grad():
        probabilities = torch.softmax(model(**encoded).logits, dim=-1)[0]
    label_index = int(torch.argmax(probabilities).item())
    labels = model.config.id2label
    label = labels.get(label_index, labels.get(str(label_index), str(label_index)))
    confidence = round(float(probabilities[label_index].item() * 100), 2)
    return str(label), confidence


# -----------------------------------------------------------------------------
# Runner notebook: pelatihan model terpilih dan pengujian contoh chat.
# -----------------------------------------------------------------------------

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
    transformer_epochs: int = 12,
    transformer_device: str = "cuda",
    transformer_options: dict[str, Any] | None = None,
    benchmark_tests: list[tuple[str, str]] | tuple[tuple[str, str], ...] | None = None,
) -> tuple[dict[str, Any], Any, Any]:
    """Latih seluruh classifier dan bandingkan holdout serta 10 chat game.

    Mengembalikan ``(artifacts, hasil_holdout, hasil_10_chat)``. Split untuk
    setiap model deterministik (random state sama), sehingga perbandingan
    holdout tidak bercampur dengan data training/tuning.
    ``benchmark_tests`` dapat mengganti 10 chat uji untuk dataset tertentu.
    """
    import time

    import pandas as pd

    test_cases = HOSTAGE_BENCHMARK_TESTS if benchmark_tests is None else tuple(benchmark_tests)
    if len(test_cases) != 10:
        raise ValueError("benchmark_tests harus berisi tepat 10 chat uji.")

    model_dir = Path(model_dir)
    transformer_config = {"epochs": transformer_epochs, "device": transformer_device}
    if transformer_options:
        reserved = {"dataset_path", "model_dir", "epochs", "device"}.intersection(transformer_options)
        if reserved:
            raise ValueError(f"Gunakan argumen utama untuk opsi: {sorted(reserved)}")
        transformer_config.update(transformer_options)
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
                    **transformer_config,
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
        for expected, chat in test_cases:
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
                "akurasi_10_chat": round(correct / len(test_cases), 2),
            }
        )

    manual_summary = pd.DataFrame(manual_rows).sort_values("benar_dari_10", ascending=False)
    return artifacts, training_summary.reset_index(drop=True), manual_summary.reset_index(drop=True)
