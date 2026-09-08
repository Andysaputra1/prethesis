"""Uji split dan fine-tuning offline dengan BERT kecil, tanpa unduhan model."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd

from modules.nlu_training import (
    _split_dataset,
    _split_transformer_dataset,
    predict_transformer_intent,
    train_transformer,
)


class TransformerTrainingTests(unittest.TestCase):
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
        split = _split_transformer_dataset(self.csv)
        train, val, test, y_train, y_val, y_test, _ = split
        self.assertFalse(set(train.index) & set(val.index))
        self.assertFalse(set(train.index) & set(test.index))
        self.assertFalse(set(val.index) & set(test.index))
        self.assertEqual(set(train.index) | set(val.index) | set(test.index), set(range(160)))
        self.assertEqual(set(y_train), set(y_val))
        self.assertEqual(set(y_val), set(y_test))
        self.assertEqual(test.tolist(), _split_dataset(self.csv)[1].tolist())
        for first, second in zip(split[:6], _split_transformer_dataset(self.csv)[:6]):
            pd.testing.assert_series_equal(first, second)

    def test_invalid_validation_size_is_rejected(self):
        for size in (0, 0.8, -0.1, 1):
            with self.assertRaises(ValueError):
                _split_transformer_dataset(self.csv, size)

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
            result = train_transformer(
                self.csv, self.root / "models", model_name=str(pretrained), device="cpu",
                epochs=5, batch_size=16, gradient_accumulation_steps=1, max_length=24,
                learning_rates=(1e-4, 2e-4), early_stopping_patience=1,
                early_stopping_threshold=1.0,
            )
        self.assertEqual(events, ["train", "train", "test"])
        summary = result["training_summary"]
        self.assertFalse(summary["test_used_for_selection"])
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
        label, confidence = predict_transformer_intent("pesan " * 100, self.root / "models", device="cpu")
        self.assertIn(label, result["label_encoder"].classes_)
        self.assertTrue(0 <= confidence <= 100)


if __name__ == "__main__":
    unittest.main()
