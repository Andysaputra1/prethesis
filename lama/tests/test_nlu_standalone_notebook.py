"""Uji fungsi langsung dari notebook; tidak mengimpor modules proyek."""
import ast
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import joblib
import numpy as np
import optuna
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.pipeline import Pipeline

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "ai_2_dataset_baru/ai_1_nlu_v3_600.ipynb"


def load_notebook():
    nb = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    namespace = {"__name__": "notebook_test"}
    for i, cell in enumerate(nb["cells"]):
        if cell["cell_type"] != "code":
            continue
        source = "".join(cell["source"])
        compile(source, f"cell_{i}", "exec")
        for node in ast.walk(ast.parse(source)):
            if isinstance(node, ast.ImportFrom):
                assert not (node.module or "").startswith("modules")
            elif isinstance(node, ast.Import):
                assert all(not alias.name.startswith("modules") for alias in node.names)
        if cell["metadata"].get("nlu_role") == "definitions":
            exec(compile(source, f"cell_{i}", "exec"), namespace)
    return namespace


class StandaloneTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ns = load_notebook()
        optuna.logging.set_verbosity(optuna.logging.WARNING)

    def test_grid_choices_preserved_and_optuna_uses_same_candidates(self):
        for kind, count in [("svm", 720), ("nb", 1920)]:
            candidates = list(self.ns["ParameterGrid"](self.ns["_classical_search_spaces"](kind)))
            self.assertEqual(len(candidates), count)
            study = optuna.create_study(sampler=optuna.samplers.RandomSampler(seed=42))
            for _ in range(15):
                trial = study.ask()
                params = self.ns["_suggest_optuna_params"](trial, kind)
                self.assertIn(params, candidates)
                study.tell(trial, 0.5)
        self.assertTrue({0.25, 0.5, 1, 2, 4, 8}.issubset(self.ns["SVM_C_VALUES"]))
        self.assertTrue({0.01, 0.05, 0.1, 0.25, 0.5, 1, 2}.issubset(self.ns["NB_ALPHA_VALUES"]))

    def test_stop_only_after_100_plus_30_and_keep_best_actual_trial(self):
        stopper = self.ns["OptunaStagnationStopper"]()
        study = optuna.create_study(direction="maximize")
        # Peningkatan kecil pada trial 110 tidak reset patience, tetapi tetap best.
        def objective(trial):
            return 0.8404 if trial.number == 109 else 0.84
        with contextlib.redirect_stdout(io.StringIO()):
            study.optimize(objective, n_trials=150, callbacks=[stopper])
        self.assertEqual(len(study.trials), 130)
        self.assertEqual(stopper.stop_reason, "stagnation")
        self.assertEqual(study.best_value, 0.8404)
        self.assertEqual(study.best_trial.number, 109)

    def test_cumulative_improvement_resets_patience_and_failed_trials_do_not_count(self):
        stopper = self.ns["OptunaStagnationStopper"](min_trials=2, patience=3, min_delta=0.001)
        study = SimpleNamespace(best_value=0.8, stopped=False)
        study.set_user_attr = lambda *a: None
        def stop():
            study.stopped = True
        study.stop = stop
        def emit(value, state="COMPLETE"):
            if state == "COMPLETE":
                study.best_value = max(study.best_value, value)
            trial = SimpleNamespace(state=SimpleNamespace(name=state), value=value)
            with contextlib.redirect_stdout(io.StringIO()):
                stopper(study, trial)
        emit(0.8)
        emit(0.8)
        emit(0.8004)
        emit(None, "FAIL")
        emit(None, "PRUNED")
        self.assertEqual(stopper.completed, 3)
        self.assertEqual(stopper.stale_trials, 1)
        emit(0.8008)
        emit(0.8012)
        self.assertEqual(stopper.stale_trials, 0)
        for _ in range(3):
            emit(0.8012)
        self.assertTrue(study.stopped)

    def test_same_estimator_and_holdout_isolation_for_both_searches(self):
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            csv = work / "data.csv"
            pd.DataFrame([
                {"teks_chat": f"{text} ronde {i} contoh{i}", "label_intent": label}
                for label, text in [("offend", "tuduhan mencurigakan"),
                                    ("defend", "pembelaan alibi"),
                                    ("neutral", "informasi malam")]
                for i in range(20)
            ]).to_csv(csv, index=False)
            train, test, _, _, _ = self.ns["_split_dataset"](csv)
            actual_spaces = self.ns["_classical_search_spaces"]
            actual_cv = self.ns["cross_val_score"]
            actual_grid = self.ns["GridSearchCV"]
            actual_evaluate = self.ns["_evaluate"]
            for kind in ["nb", "svm"]:
                def small_space(k):
                    space = actual_spaces(k)[0]
                    return [{key: values[:1] for key, values in space.items()}]
                def inspect_estimator(model):
                    if kind == "svm":
                        self.assertIsInstance(model, CalibratedClassifierCV)
                        self.assertIsInstance(model.estimator, Pipeline)
                        self.assertEqual(model.estimator.named_steps["svm"].max_iter, 10000)
                    else:
                        self.assertIsInstance(model, Pipeline)
                def checked_cv(model, x, y, **kw):
                    inspect_estimator(model)
                    self.assertEqual(x.tolist(), train.tolist())
                    self.assertFalse(set(x) & set(test))
                    return actual_cv(model, x, y, **kw)
                def checked_grid(model, *args, **kw):
                    inspect_estimator(model)
                    return actual_grid(model, *args, **kw)
                evaluations = []
                def checked_evaluate(model, x, y, title):
                    self.assertEqual(x.tolist(), test.tolist())
                    evaluations.append(title)
                    return actual_evaluate(model, x, y, title)
                with patch.dict(self.ns, {
                    "_classical_search_spaces": small_space,
                    "cross_val_score": checked_cv,
                    "GridSearchCV": checked_grid,
                    "_evaluate": checked_evaluate,
                }), contextlib.redirect_stdout(io.StringIO()):
                    grid = self.ns["_train_classical_grid"](csv, work, f"{kind}_grid.pkl", kind, 2, 1)
                    tuned = self.ns["_train_classical_optuna"](
                        csv, work, f"{kind}_optuna.pkl", model_kind=kind,
                        n_trials=5, cv_folds=2, timeout=None, n_jobs=1,
                        min_trials=2, patience=2, min_delta=0.001,
                    )
                self.assertEqual(len(evaluations), 2)
                self.assertEqual(tuned["training_summary"]["stop_reason"], "stagnation")
                for result in [grid, tuned]:
                    model = joblib.load(result["model_path"])
                    self.assertEqual(model.predict_proba(test).shape, (12, 3))
                    run_dir = Path(result["run_dir"])
                    split = json.loads((run_dir / "split_indices.json").read_text())
                    self.assertFalse(set(split["train"]) & set(split["test"]))
                    summary = json.loads((run_dir / "summary.json").read_text())
                    self.assertFalse(summary["test_used_for_selection"])
                self.assertTrue((Path(grid["run_dir"]) / "cv_results.csv").exists())
                self.assertEqual(len(pd.read_csv(Path(tuned["run_dir"]) / "trials.csv")), 4)

    def test_budget_validation(self):
        trainer = self.ns["train_naive_bayes_optuna"]
        for options in [{"n_trials": 50}, {"patience": 0}, {"min_delta": -1}, {"timeout": 0}]:
            with self.assertRaises(ValueError):
                trainer("missing.csv", "unused", **options)


class TransformerTrainingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ns = load_notebook()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.csv = self.root / "data.csv"
        pd.DataFrame([
            {"teks_chat": f"pesan intent {label} contoh {i}", "label_intent": f"intent_{label}"}
            for label in range(8) for i in range(20)
        ]).to_csv(self.csv, index=False)

    def test_splits_are_disjoint_reproducible_and_preserve_classical_test(self):
        split = self.ns["_split_transformer_dataset"](self.csv)
        train, val, test, y_train, y_val, y_test, _ = split
        self.assertFalse(set(train.index) & set(val.index))
        self.assertFalse(set(train.index) & set(test.index))
        self.assertFalse(set(val.index) & set(test.index))
        self.assertEqual(set(train.index) | set(val.index) | set(test.index), set(range(160)))
        self.assertEqual(set(y_train), set(y_val))
        self.assertEqual(set(y_val), set(y_test))
        self.assertEqual(test.tolist(), self.ns["_split_dataset"](self.csv)[1].tolist())
        for first, second in zip(split[:6], self.ns["_split_transformer_dataset"](self.csv)[:6]):
            pd.testing.assert_series_equal(first, second)

    def test_invalid_validation_size_is_rejected(self):
        for size in (0, 0.8, -0.1, 1):
            with self.assertRaises(ValueError):
                self.ns["_split_transformer_dataset"](self.csv, size)

    def test_real_training_selects_on_validation_and_predicts_test_once(self):
        import torch
        from transformers import BertConfig, BertForSequenceClassification, BertTokenizerFast, Trainer

        torch.set_num_threads(1)
        pretrained = self.root / "tiny_bert"
        pretrained.mkdir()
        (pretrained / "vocab.txt").write_text(
            "[PAD]\n[UNK]\n[CLS]\n[SEP]\n[MASK]\npesan\nintent\ncontoh\n", encoding="utf-8",
        )
        BertTokenizerFast(vocab_file=str(pretrained / "vocab.txt")).save_pretrained(pretrained)
        BertForSequenceClassification(BertConfig(
            vocab_size=8, hidden_size=16, num_hidden_layers=1, num_attention_heads=2,
            intermediate_size=32, max_position_embeddings=32, num_labels=8,
        )).save_pretrained(pretrained)

        events = []
        original_train, original_predict = Trainer.train, Trainer.predict

        def track_train(trainer, *args, **kwargs):
            self.assertEqual(len(trainer.train_dataset), 104)
            self.assertEqual(len(trainer.eval_dataset), 24)
            self.assertTrue(all(p.requires_grad for p in trainer.model.parameters()))
            events.append("train")
            return original_train(trainer, *args, **kwargs)

        def track_predict(trainer, dataset, *args, **kwargs):
            self.assertEqual(events, ["train", "train"])
            self.assertEqual(len(dataset), 32)
            events.append("test")
            return original_predict(trainer, dataset, *args, **kwargs)

        with patch.object(Trainer, "train", track_train), patch.object(Trainer, "predict", track_predict):
            result = self.ns["train_transformer"](
                self.csv, self.root / "models", model_name=str(pretrained), device="cpu",
                epochs=5, batch_size=16, gradient_accumulation_steps=1, max_length=24,
                learning_rates=(1e-4, 2e-4), early_stopping_patience=1,
                early_stopping_threshold=1.0,
            )
        self.assertEqual(events, ["train", "train", "test"])
        summary = result["training_summary"]
        self.assertFalse(summary["test_used_for_selection"])
        self.assertEqual(summary["precision"], "fp32")
        self.assertEqual(summary["optimizer"], "adamw_torch")
        self.assertEqual(len(summary["trials"]), 2)
        self.assertTrue(all(t["epochs_trained"] == 2 for t in summary["trials"]))
        self.assertEqual(summary["best_trial"]["best_validation_f1_macro"], max(
            t["best_validation_f1_macro"] for t in summary["trials"]
        ))
        saved = Path(result["model_path"])
        self.assertEqual(json.loads((saved / "training_summary.json").read_text())["max_length"], 24)
        self.assertEqual(len(pd.read_csv(saved / "test_predictions.csv")), 32)
        self.assertEqual(sum(map(sum, result["metrics"]["confusion_matrix"])), 32)
        # Input panjang harus menggunakan max_length hasil training, bukan hardcoded 128.
        label, confidence = self.ns["predict_transformer_intent"]("pesan " * 100, self.root / "models", device="cpu")
        self.assertIn(label, result["label_encoder"].classes_)
        self.assertTrue(0 <= confidence <= 100)


if __name__ == "__main__":
    unittest.main()
