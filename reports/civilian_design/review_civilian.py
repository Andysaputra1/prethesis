"""Review dua notebook Civilian secara lokal; tidak melatih model atau memanggil API."""

import ast
import hashlib
import json
import os
import re
from pathlib import Path

import nbformat
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / "ai_2_dataset_baru"
REPORT = ROOT / "reports/civilian_design"


def read_runtime(path):
    nb = nbformat.read(path, as_version=4)
    nbformat.validate(nb)
    scope = {}
    for cell in nb.cells:
        if cell.cell_type != "code":
            continue
        if "# Metadata contoh" in cell.source:
            break
        exec(compile(cell.source, str(path), "exec"), scope)
    return nb, scope


def event(scope, event_id, speaker, text, intent, **updates):
    targets, source = scope["extract_targets"](text, intent, speaker, scope["PLAYERS"])
    result = {
        "id": event_id, "speaker": speaker, "text": text, "intent": intent,
        "confidence": 1.0, "targets": targets, "target_source": source,
        "round": 1, "phase": "day", "time": 10.0,
    }
    result.update(updates)
    return result


def main():
    os.chdir(WORK)
    results = []
    runtimes = {}
    observations = {}
    for method in ["utility_ai", "behavior_tree"]:
        nb, scope = read_runtime(WORK / f"civilian_{method}.ipynb")
        runtimes[method] = scope
        for cell in nb.cells:
            if cell.cell_type == "code":
                ast.parse(cell.source)
                assert cell.execution_count is not None
                assert not any(output.output_type == "error" for output in cell.outputs)
                for output in cell.outputs:
                    html = output.get("data", {}).get("text/html", "")
                    assert not re.search(r"<td[^>]*>\s*(NaN|nan)\s*</td>", html)
        results.append(f"{method}: notebook lengkap dieksekusi, valid, dan tabel tanpa NaN.")

        view = {
            "players": scope["PLAYERS"], "ai": "AI", "round": 1, "phase": "day",
            "day_start": 0.0, "now": 30.0, "can_chat": True,
        }
        events = [
            event(scope, "1", "A", "Vote AI", "offend"),
            event(scope, "2", "B", "Dia sus", "offend"),
            event(scope, "3", "C", "Kamu sus", "offend"),
        ]
        table, context = scope["build_features"](events, view)
        chosen, _ = scope["choose_action"](table, context, view)
        observations[method] = chosen
        json.dumps(scope["prepare_nlg"](chosen), allow_nan=False)

        empty_table, empty_context = scope["build_features"]([], view)
        empty_decision, _ = scope["choose_action"](empty_table, empty_context, view)
        assert empty_decision["target"] is None
        json.dumps(scope["prepare_nlg"](empty_decision), allow_nan=False)

        # Event masa depan, malam, atau pengirim di luar roster tidak menambah tekanan.
        ignored = [
            dict(events[0], id="future", time=100.0),
            dict(events[0], id="night", phase="night"),
            dict(events[0], id="outsider", speaker="UNKNOWN"),
        ]
        ignored_table, _ = scope["build_features"](ignored, view)
        assert ignored_table["pressure"].sum() == 0

        # Ucapan AI dan tuduhan diri tidak menjadi penguat tuduhan eksternal.
        self_events = [
            event(scope, "ai_msg", "AI", "Vote B", "offend"),
            event(scope, "self_msg", "B", "Vote aku", "offend"),
        ]
        self_table, _ = scope["build_features"](self_events, view)
        assert self_table["pressure"].sum() == 0
        assert scope["extract_targets"]("Raka bukan Hitman", "defend", "Sinta", ["Raka", "Sinta"])[0] == ["Raka"]
        results.append(f"{method}: JSON valid, target kosong None, nama baru, batas waktu/roster, dan anti-penguatan diri lulus.")

    assert observations["utility_ai"]["action"] == "defend_self"
    assert observations["behavior_tree"]["action"] == "ask_information"
    results.append("Perbedaan metode terverifikasi: satu tuduhan AI + dua target ambigu -> Utility membela diri, BT klarifikasi.")

    # Perhitungan pengamatan dan ekstraksi target identik agar perbandingan metode adil.
    for function in ["extract_targets", "build_features", "annotate_event", "chat_permission", "predict_nlu"]:
        a = runtimes["utility_ai"][function].__code__
        b = runtimes["behavior_tree"][function].__code__
        assert a.co_code == b.co_code
    results.append("Jalur NLU, ekstraksi target, parameter, dan izin aksi sama pada kedua metode.")

    # Pemeriksaan kompatibilitas semua file model klasik, tanpa klaim akurasi dari contoh tunggal.
    scope = runtimes["utility_ai"]
    for model_path in sorted((WORK / "models/notebook_standalone").glob("*.pkl")):
        if not model_path.name.startswith(("intent_classifier_svm", "intent_classifier_nb")):
            continue
        scope["MODEL_FILENAME"] = model_path.name
        runtime = scope["load_nlu"]("classical")
        label, confidence = scope["predict_nlu"]("B bukan Hitman", runtime)
        assert label in {"offend", "defend", "neutral"} and 0 <= confidence <= 1
        results.append(f"NLU lokal {model_path.name}: inferensi berhasil (cek integrasi, bukan akurasi).")

    model_dir = WORK / "models/notebook_standalone/intent_classifier_transformer"
    if model_dir.is_dir():
        runtime = scope["load_nlu"]("indobert")
        label, confidence = scope["predict_nlu"]("B bukan Hitman", runtime)
        assert label in {"offend", "defend", "neutral"} and 0 <= confidence <= 1
        results.append("IndoBERT lokal: inferensi CPU berhasil, local_files_only=True.")
    else:
        results.append("IndoBERT belum diuji: model lokal tidak tersedia.")

    hashes = json.loads((REPORT / "original_hashes.json").read_text(encoding="utf-8"))
    for relative, expected in hashes.items():
        actual = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
        assert actual == expected, f"File lama berubah: {relative}"
    results.append("Hash fuzzy Janice, fuzzy dataset baru, dan nlu_baru tetap sama.")
    report = (
        "# Review Civilian — Utility AI dan Behavior Tree\n\n"
        "Dua notebook baru; cakupan keputusan chat Civilian. Tidak ada training ulang, panggilan LLM/API, "
        "atau pengiriman dataset. Semua notebook berhasil dijalankan berurutan dengan model lokal.\n\n"
        + "\n".join(f"- {result}" for result in results)
        + "\n\n## Batas hasil\n\n"
        "Ini prototipe kebijakan, bukan strategi terbaik yang sudah terbukti. Tidak ada evaluasi win rate "
        "atau akurasi ekstraksi target pada test beranotasi. Bobot dan threshold masih pilihan desain; "
        "tekanan sosial bukan probabilitas Hitman. Resolver aturan abstain pada banyak kalimat majemuk "
        "dan kata ganti, dan masih bisa salah pada bahasa di luar pola. Voting, skill, klaim role, "
        "kontradiksi, penjadwal chat, dan pemanggilan LLM belum diintegrasikan. "
        "can_chat hanya milik AI sendiri; tidak ada pembacaan status korban pemain lain.\n\n"
        "## Cara menjalankan\n\n"
        "Buka notebook di ai_2_dataset_baru, gunakan kernel venv proyek, lalu Run All dari folder tersebut. "
        "Atur PLAYERS dan metadata contoh sesuai event game. Model klasifikasi sudah lokal; "
        "jangan menjalankan ulang notebook training hanya untuk mencoba kebijakan.\n"
    )
    (REPORT / "review.md").write_text(report, encoding="utf-8")
    print("\n".join(results), flush=True)


if __name__ == "__main__":
    main()
