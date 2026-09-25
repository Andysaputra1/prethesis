"""Uji Optuna dengan data kecil: isolasi test, kalibrasi, dan artefak."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import joblib
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.pipeline import Pipeline

from lama.modules import nlu_training as nt


class OptunaTrainingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.csv = self.root / "dataset.csv"
        rows = [
            {"teks_chat": f"{text} ronde {i} pemain contoh{i}", "label_intent": label}
            for label, text in [
                ("offend", "kamu mencurigakan tuduhan"),
                ("defend", "aku membela alibi"),
                ("neutral", "fase malam informasi"),
            ]
            for i in range(20)
        ]
        pd.DataFrame(rows).to_csv(self.csv, index=False)

    def test_both_models_keep_test_out_of_search_and_save_predictable_models(self):
        expected_train, expected_test, _, _, _ = nt._split_dataset(self.csv)
        original_cv = nt.cross_val_score
        for kind, trainer in [
            ("nb", nt.train_naive_bayes_optuna),
            ("svm", nt.train_svm_optuna),
        ]:
            with self.subTest(kind=kind):
                calls = []

                def inspect_cv(estimator, x, y, **kwargs):
                    self.assertEqual(x.tolist(), expected_train.tolist())
                    self.assertFalse(set(x) & set(expected_test))
                    for train_idx, val_idx in kwargs["cv"]:
                        self.assertFalse(set(train_idx) & set(val_idx))
                    if kind == "svm":
                        self.assertIsInstance(estimator, CalibratedClassifierCV)
                        self.assertIsInstance(estimator.estimator, Pipeline)
                    calls.append(1)
                    return original_cv(estimator, x, y, **kwargs)

                with patch.object(nt, "cross_val_score", side_effect=inspect_cv), patch.object(
                    nt, "_evaluate", wraps=nt._evaluate
                ) as evaluate:
                    result = trainer(
                        self.csv, self.root / kind, n_trials=2, cv_folds=2, n_jobs=1,
                    )
                self.assertEqual(len(calls), 2)
                evaluate.assert_called_once()
                self.assertEqual(evaluate.call_args.args[1].tolist(), expected_test.tolist())
                self.assertEqual(len(result["study"].trials), 2)
                saved = joblib.load(result["model_path"])
                self.assertEqual(len(saved.predict(expected_test)), len(expected_test))
                self.assertEqual(saved.predict_proba(expected_test).shape, (12, 3))
                label, confidence = nt.predict_intent(
                    "aku membela alibi", self.root / kind, Path(result["model_path"]).name,
                )
                self.assertIn(label, {"offend", "defend", "neutral"})
                self.assertTrue(0 <= confidence <= 100)
                run_dir = Path(result["run_dir"])
                summary = json.loads((run_dir / "summary.json").read_text())
                self.assertFalse(summary["test_used_for_selection"])
                self.assertEqual(len(pd.read_csv(run_dir / "trials.csv")), 2)
                indices = json.loads((run_dir / "split_indices.json").read_text())
                self.assertFalse(set(indices["train"]) & set(indices["test"]))

    def test_word_and_character_svm_spaces_work(self):
        import optuna
        for analyzer in ["word", "char_wb"]:
            choices = {
                "analyzer": analyzer, "word_ngram_max": 2, "char_ngram_max": 5,
                "min_df": 1, "max_df": 1.0, "sublinear_tf": True,
                "C": 1.0, "class_weight": "balanced",
            }
            params = nt._suggest_optuna_params(optuna.trial.FixedTrial(choices), "svm")
            model = nt._build_optuna_model("svm", params, 2)
            x, _, y, _, _ = nt._split_dataset(self.csv)
            model.fit(x, y)
            self.assertEqual(len(model.predict(x)), len(x))

    def test_invalid_budgets_fail_before_reading_dataset(self):
        for trainer in [nt.train_svm_optuna, nt.train_naive_bayes_optuna]:
            for options in [{"n_trials": 0}, {"cv_folds": 1}, {"timeout": -1}, {"n_jobs": 0}]:
                with self.assertRaises(ValueError):
                    trainer("missing.csv", self.root, **options)


if __name__ == "__main__":
    unittest.main()
