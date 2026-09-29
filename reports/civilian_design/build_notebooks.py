import ast
import copy
import hashlib
import json
from pathlib import Path
import nbformat as nbf

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'ai_2_dataset_baru'

IMPORTS = """from pathlib import Path
import math
import re

import joblib
import numpy as np
import pandas as pd
from IPython.display import display
"""
CONFIG = """# Jalankan notebook dari folder ai_2_dataset_baru.
MODEL_DIR = Path("models/notebook_standalone")
NLU_BACKEND = "classical"
MODEL_FILENAME = "intent_classifier_svm.pkl"

# Contoh roster publik; ganti dengan ID pemain dari game.
PLAYERS = ["AI", "A", "B", "C", "D", "E"]
AI_NAME = "AI"

# Nilai awal rancangan, belum hasil optimasi pertandingan.
MIN_INTENT_CONFIDENCE = 0.60
MIN_ACCUSERS = 2
MIN_PRESSURE = 0.50
SILENCE_SECONDS = 60.0
MIN_MESSAGES = 3
"""
LOAD = """# Memuat model lokal hasil nlu_baru sekali, tanpa training atau unduhan.
def load_nlu(backend=NLU_BACKEND):
    if backend == "classical":
        path = MODEL_DIR / MODEL_FILENAME
        if not path.is_file():
            raise FileNotFoundError(f"Model tidak ditemukan: {path}. Periksa MODEL_DIR dan MODEL_FILENAME.")
        return {"backend": backend, "model": joblib.load(path)}

    if backend == "indobert":
        import torch
        from transformers import AutoModelForSequenceClassification, AutoTokenizer

        path = MODEL_DIR / "intent_classifier_transformer"
        if not path.is_dir():
            raise FileNotFoundError(f"Model IndoBERT lokal tidak ditemukan: {path}")
        model = AutoModelForSequenceClassification.from_pretrained(path, local_files_only=True)
        model.eval()
        return {
            "backend": backend, "model": model,
            "tokenizer": AutoTokenizer.from_pretrained(path, local_files_only=True),
            "torch": torch,
        }

    raise ValueError("NLU_BACKEND harus classical atau indobert.")
"""
PREDICT = """# Mengubah satu chat menjadi label dan confidence 0-1; ini bukan peluang role Hitman.
def predict_nlu(text, runtime):
    model = runtime["model"]
    if runtime["backend"] == "classical":
        label = str(model.predict([text])[0])
        confidence = float(np.max(model.predict_proba([text])[0]))
    else:
        encoded = runtime["tokenizer"](
            text, return_tensors="pt", truncation=True,
            max_length=getattr(model.config, "nlu_max_length", 128),
        )
        with runtime["torch"].inference_mode():
            probabilities = runtime["torch"].softmax(model(**encoded).logits, dim=-1)[0]
        index = int(probabilities.argmax())
        label = str(model.config.id2label[index])
        confidence = float(probabilities[index])

    label = {"offense": "offend", "defense": "defend"}.get(label, label)
    if label not in {"offend", "defend", "neutral"}:
        raise ValueError(f"Label model tidak sesuai: {label}")
    return label, confidence
"""
TARGET = r'''# Mengambil target dengan pola eksplisit; nama yang sekadar disebut tidak otomatis menjadi target.
def extract_targets(text, intent, speaker, players, reply_to=None):
    if intent == "neutral":
        return [], "neutral"

    # Kutipan dan kalimat bersyarat belum aman disimpulkan dengan aturan sederhana.
    if re.search(r"[\"“”]|\b(kalau|jika|seandainya|katanya|bilang|kata|bukan berarti)\b", text, re.I):
        return [], "tidak_diketahui"

    # Pola terbatas; sengaja tidak menebak semua negasi, sarkasme, atau konteks lintas pesan.
    def matches(subject):
        if intent == "offend":
            patterns = [
                rf"\b(?:curiga|mencurigai|tuduh|menuduh|vote|voting|pilih|eksekusi)\s+(?:si\s+)?{subject}",
                rf"{subject}\s+(?:(?:itu|adalah|pasti|jelas|sangat|paling|memang|si)\s+)*(?:hitman|pelaku|mencurigakan|sus|bohong|berbohong)\b",
            ]
            for pattern in patterns:
                for match in re.finditer(pattern, text, re.I):
                    prefix = text[max(0, match.start() - 35):match.start()]
                    if not re.search(r"\b(?:jangan|tidak|tak|bukan|gak|nggak|ga)(?:\s+\w+){0,2}\s*$", prefix, re.I):
                        return True
            return False

        patterns = [
            rf"{subject}\s+(?:itu\s+)?(?:bukan\s+(?:hitman|pelaku)|tidak\s+bersalah|tak\s+bersalah)\b",
            rf"\b(?:bela|membela)\s+(?:si\s+)?{subject}",
            rf"\bjangan\s+(?:tuduh|menuduh|vote|eksekusi)\s+(?:si\s+)?{subject}",
        ]
        for pattern in patterns:
            for match in re.finditer(pattern, text, re.I):
                prefix = text[max(0, match.start() - 35):match.start()]
                if not re.search(r"\b(?:tidak|tak|bukan|gak|nggak|ga)(?:\s+\w+){0,2}\s*$", prefix, re.I):
                    return True
        return False

    targets = []
    for player in players:
        subject = rf"(?<!\w){re.escape(player)}(?!\w)"
        if matches(subject):
            targets.append(player)

    if matches(r"\b(?:aku|saya|gw|gue|gua)\b"):
        targets.append(speaker)

    # reply_to adalah ID pengirim pesan yang dibalas, bukan tebakan dari teks.
    if matches(r"\b(?:kamu|lu|lo|elu)\b"):
        if reply_to in players:
            targets.append(reply_to)
        else:
            return [], "tidak_diketahui"

    # Jangan pakai reply-to untuk menebak 'dia/mereka'.
    if re.search(r"\b(dia|mereka)\b", text, re.I):
        return [], "tidak_diketahui"

    # Nama tambahan yang belum terselesaikan membuat chat multi-target ini ambigu.
    mentioned = [p for p in players if re.search(rf"(?<!\w){re.escape(p)}(?!\w)", text, re.I)]
    if any(p not in targets for p in mentioned):
        return [], "tidak_diketahui"

    targets = sorted(set(targets))
    return targets, "aturan_teks" if targets else "tidak_diketahui"
'''
EVENT = """# Menyatukan metadata publik, prediksi NLU, dan target; field rahasia tidak disalin.
def annotate_event(event, runtime, players):
    intent, confidence = predict_nlu(event["text"], runtime)
    targets, source = extract_targets(
        event["text"], intent, event["speaker"], players, event.get("reply_to"),
    )
    return {
        "id": event["id"], "speaker": event["speaker"], "text": event["text"],
        "round": event["round"], "phase": event["phase"], "time": event["time"],
        "intent": intent, "confidence": confidence,
        "targets": targets, "target_source": source,
    }
"""
FEATURES = """# Menghitung pengamatan ronde siang saat ini, tanpa role atau status korban tersembunyi.
def build_features(events, view):
    players = sorted(view["players"])
    ai = view["ai"]
    seen = set()
    current = []
    for event in events:
        if (event["round"] != view["round"] or event["phase"] != "day"
                or not view["day_start"] <= event["time"] <= view["now"]
                or event["speaker"] not in players or event["id"] in seen):
            continue
        seen.add(event["id"])
        current.append(event)

    # Chat AI sendiri tidak menjadi dukungan bagi keputusannya sendiri.
    observed = [event for event in current if event["speaker"] != ai]
    uncertain = [event for event in observed if (
        not math.isfinite(event["confidence"])
        or event["confidence"] < MIN_INTENT_CONFIDENCE
        or (event["intent"] != "neutral" and not event["targets"])
    )]
    trusted = [event for event in observed if (
        math.isfinite(event["confidence"])
        and event["confidence"] >= MIN_INTENT_CONFIDENCE
        and event["targets"]
    )]

    rows = []
    for player in players:
        # Satu pengirim paling banyak satu hitungan per intent dan target per ronde.
        accusers = {event["speaker"] for event in trusted if (
            event["intent"] == "offend" and player in event["targets"]
            and event["speaker"] != player
        )}
        defenders = {event["speaker"] for event in trusted if (
            event["intent"] == "defend" and player in event["targets"]
            and event["speaker"] != player
        )}
        eligible = len([p for p in players if p not in {ai, player}])
        messages = [event for event in current if event["speaker"] == player]
        last_time = max([view["day_start"], *[event["time"] for event in messages]])
        silence = min(1.0, max(0.0, view["now"] - last_time) / SILENCE_SECONDS)
        rows.append({
            "player": player, "accusers": len(accusers), "defenders": len(defenders),
            "pressure": len(accusers) / max(1, eligible),
            "support": len(defenders) / max(1, eligible),
            "silence": silence, "chat_count": len(messages),
            "accuser_names": sorted(accusers), "defender_names": sorted(defenders),
        })

    context = {
        "uncertainty": len(uncertain) / max(1, len(observed)),
        "few_messages": len(observed) < MIN_MESSAGES,
        "message_count": len(observed),
    }
    return pd.DataFrame(rows), context
"""
GUARD = """# Menghalangi chat ketika fase atau izin bicara AI sendiri tidak mengizinkan.
def chat_permission(view):
    if view["phase"] != "day":
        return {"action": "wait", "intent": None, "target": None, "reason": "Bukan fase diskusi siang."}
    if not view["can_chat"]:
        return {"action": "wait", "intent": None, "target": None, "reason": "AI tidak memiliki izin mengirim chat."}
    return None
"""
REPORT = """# Menampilkan tabel dengan angka ringkas dan tanda kosong, tanpa mengubah data perhitungan.
def show_table(table):
    display(table.style.format(
        precision=3, na_rep="—", escape="html",
    ).hide(axis="index").set_properties(**{
        "white-space": "normal", "max-width": "420px", "text-align": "left",
    }))
"""
HANDOFF = """# Menyiapkan instruksi percakapan dari keputusan; tidak memanggil LLM/API.
def prepare_nlg(decision):
    return {
        "send_chat": decision["action"] != "wait",
        "intent": decision["intent"], "target": decision["target"],
        "action": decision["action"], "basis": decision["reason"],
        "constraints": [
            "Pertahankan intent dan target keputusan; jangan memilih target baru.",
            "Jangan mengklaim mengetahui role, hasil Peek, atau identitas korban tersembunyi.",
            "Tuduhan sosial bukan fakta role; sampaikan kecurigaan sebagai dugaan.",
            "Pembelaan pemain lain meminta evaluasi yang adil, bukan memastikan ia warga.",
        ],
    }
"""
SIMULATION = """# Metadata contoh berasal dari pengamatan publik dan izin bicara AI sendiri.
view = {
    "players": PLAYERS, "ai": AI_NAME, "round": 1, "phase": "day",
    "day_start": 0.0, "now": 45.0, "can_chat": True,
}

# Label contoh ditetapkan untuk menguji kebijakan, bukan hasil akurasi NLU.
demo_specs = [
    ("e1", "A", "AI pasti Hitman", "offend", 10.0),
    ("e2", "B", "Vote AI", "offend", 15.0),
    ("e3", "C", "D pasti Hitman", "offend", 20.0),
    ("e4", "E", "Vote D", "offend", 25.0),
    ("e5", "B", "D bukan Hitman", "defend", 30.0),
]
demo_events = []
for event_id, speaker, text, intent, moment in demo_specs:
    targets, source = extract_targets(text, intent, speaker, PLAYERS)
    demo_events.append({
        "id": event_id, "speaker": speaker, "text": text, "round": 1,
        "phase": "day", "time": moment, "intent": intent, "confidence": 1.0,
        "targets": targets, "target_source": source,
    })

features, context = build_features(demo_events, view)
display(features)
display(pd.DataFrame([context]))
"""
INTEGRATION = """# Menguji model NLU tersimpan dan resolver target lokal, tanpa training atau API.
runtime = load_nlu()
live_events = [
    annotate_event({
        "id": event_id, "speaker": speaker, "text": text,
        "round": 1, "phase": "day", "time": moment,
    }, runtime, PLAYERS)
    for event_id, speaker, text, _, moment in demo_specs
]
display(pd.DataFrame(live_events)[[
    "speaker", "text", "intent", "confidence", "targets", "target_source",
]])
live_features, live_context = build_features(live_events, view)
live_decision, live_trace = choose_action(live_features, live_context, view)
display(pd.DataFrame([live_decision]))
display(live_trace)
"""

UTILITY_CONFIG = """# Bobot awal utilitas: skor kesesuaian tindakan, bukan probabilitas kebenaran.
UTILITY_WEIGHTS = {
    "ask_base": 0.30, "ask_uncertainty": 0.35, "ask_few_messages": 0.15,
    "self_base": 0.45, "self_pressure": 0.55,
    "defend_base": 0.20, "defend_pressure": 0.35, "defend_support": 0.35,
    "challenge_base": 0.25, "challenge_pressure": 0.60,
    "silence_base": 0.20, "silence_weight": 0.25,
}
"""
UTILITY = """# Menghitung semua tindakan yang layak, lalu memilih skor tertinggi dengan urutan seri tetap.
def choose_action(features, context, view):
    blocked = chat_permission(view)
    if blocked is not None:
        return blocked, pd.DataFrame([blocked])

    weights = UTILITY_WEIGHTS
    candidates = [{
        "action": "ask_information", "intent": "neutral", "target": None,
        "score": weights["ask_base"] + weights["ask_uncertainty"] * context["uncertainty"]
                 + weights["ask_few_messages"] * context["few_messages"],
        "reason": "Meminta informasi; ketidakjelasan atau data sedikit menambah prioritas.",
    }]

    for row in features.sort_values("player").to_dict("records"):
        player = row["player"]
        if player == view["ai"]:
            if row["accusers"] > 0:
                candidates.append({
                    "action": "defend_self", "intent": "defend", "target": player,
                    "score": weights["self_base"] + weights["self_pressure"] * row["pressure"],
                    "reason": f'{row["accusers"]} pemain berbeda menuduh AI dalam ronde ini.',
                })
            continue

        # Pembelaan ini menyeimbangkan diskusi; dukungan pemain lain bukan bukti ia warga.
        if row["accusers"] > 0 and row["defenders"] > 0:
            candidates.append({
                "action": "defend_player", "intent": "defend", "target": player,
                "score": weights["defend_base"] + weights["defend_pressure"] * row["pressure"]
                         + weights["defend_support"] * row["support"],
                "reason": f'{player} menerima tuduhan dan pembelaan; minta penilaian yang adil.',
            })

        # Tantangan berupa dugaan sosial, bukan vonis Hitman; perlu beberapa penuduh berbeda.
        if (row["accusers"] >= MIN_ACCUSERS and row["pressure"] >= MIN_PRESSURE
                and row["defenders"] == 0):
            candidates.append({
                "action": "challenge_player", "intent": "offend", "target": player,
                "score": weights["challenge_base"] + weights["challenge_pressure"] * row["pressure"],
                "reason": f'{player} mendapat tuduhan dari {row["accusers"]} pemain berbeda; belum bukti role.',
            })

        # Diam hanya memicu ajakan bicara, tidak menambah skor tuduhan.
        if row["silence"] >= 1.0:
            candidates.append({
                "action": "ask_quiet_player", "intent": "neutral", "target": player,
                "score": weights["silence_base"] + weights["silence_weight"] * row["silence"],
                "reason": f'{player} belum chat selama minimal {SILENCE_SECONDS:g} detik siang; sebabnya tidak diketahui.',
            })

    # Pembulatan pembanding mencegah selisih floating point memutus seri secara tidak sengaja.
    ranked = sorted(candidates, key=lambda item: round(item["score"], 12), reverse=True)
    chosen = {key: value for key, value in ranked[0].items() if key != "score"}
    return chosen, pd.DataFrame(ranked)
"""
BT_CONFIG = """# Selector memeriksa Sequence dari atas; setiap Sequence berisi kondisi lalu aksi.
BEHAVIOR_TREE = [
    {"condition": "unclear", "action": "ask_information"},
    {"condition": "self_accused", "action": "defend_self"},
    {"condition": "contested_player", "action": "defend_player"},
    {"condition": "strong_pressure", "action": "challenge_player"},
    {"condition": "quiet_player", "action": "ask_quiet_player"},
    {"condition": "always", "action": "ask_information"},
]

# Bila setengah pengamatan tidak jelas, klarifikasi didahulukan.
UNCERTAINTY_LIMIT = 0.50
"""
BT = """# Menjalankan Selector berisi Sequence kondisi-aksi; aksi pertama yang lolos dipilih.
def choose_action(features, context, view):
    blocked = chat_permission(view)
    if blocked is not None:
        return blocked, pd.DataFrame([{"node": "izin_chat", "status": "blocked", **blocked}])

    self_row = features.loc[features["player"] == view["ai"]].iloc[0]
    others = features.loc[features["player"] != view["ai"]].sort_values(
        ["pressure", "support", "player"], ascending=[False, False, True], kind="stable",
    )
    contested = others.loc[(others["accusers"] > 0) & (others["defenders"] > 0)]
    suspected = others.loc[
        (others["accusers"] >= MIN_ACCUSERS) & (others["pressure"] >= MIN_PRESSURE)
        & (others["defenders"] == 0)
    ]
    quiet = others.loc[others["silence"] >= 1.0].sort_values(
        ["silence", "player"], ascending=[False, True], kind="stable",
    )

    # Calon target berasal dari tabel pengamatan, bukan role asli atau keluaran LLM.
    conditions = {
        "unclear": context["uncertainty"] >= UNCERTAINTY_LIMIT,
        "self_accused": self_row["accusers"] > 0,
        "contested_player": not contested.empty,
        "strong_pressure": not suspected.empty,
        "quiet_player": not quiet.empty,
        "always": True,
    }
    actions = {
        "ask_information": {
            "intent": "neutral", "target": None,
            "reason": "Meminta informasi sebelum membuat tuduhan lebih lanjut.",
        },
        "defend_self": {
            "intent": "defend", "target": view["ai"],
            "reason": f'{int(self_row["accusers"])} pemain berbeda menuduh AI dalam ronde ini.',
        },
        "defend_player": {
            "intent": "defend", "target": None if contested.empty else contested.iloc[0]["player"],
            "reason": "Ada tuduhan dan pembelaan; minta penilaian adil tanpa memastikan role.",
        },
        "challenge_player": {
            "intent": "offend", "target": None if suspected.empty else suspected.iloc[0]["player"],
            "reason": "Beberapa pemain menuduh target yang sama; ini dugaan sosial, belum bukti Hitman.",
        },
        "ask_quiet_player": {
            "intent": "neutral", "target": None if quiet.empty else quiet.iloc[0]["player"],
            "reason": "Mengajak pemain diam berbicara tanpa menebak penyebab diam.",
        },
    }

    trace = []
    for sequence in BEHAVIOR_TREE:
        passed = bool(conditions[sequence["condition"]])
        trace.append({
            "condition": sequence["condition"], "action": sequence["action"],
            "status": "success" if passed else "failure",
        })
        if passed:
            action = sequence["action"]
            return {"action": action, **actions[action]}, pd.DataFrame(trace)

    raise RuntimeError("Behavior Tree perlu cabang always agar selalu memiliki tindakan cadangan.")
"""
SCENARIOS = """# Memeriksa keputusan pada situasi yang bisa ditentukan tanpa mengetahui role rahasia.
ambiguous_events = [
    dict(demo_events[0], id="unknown_1", speaker="C", text="Dia sus", targets=[]),
    dict(demo_events[0], id="unknown_2", speaker="E", text="Kamu sus", targets=[]),
]
scenario_results = []
for name, scenario_events, scenario_view in [
    ("Tidak ada chat", [], view),
    ("AI dituduh", demo_events[:2], view),
    ("Tuduhan dan pembelaan D", demo_events[2:], view),
    ("D dituduh dua pemain", demo_events[2:4], view),
    ("Fase malam", demo_events, {**view, "phase": "night"}),
    ("AI tidak bisa chat", demo_events, {**view, "can_chat": False}),
    ("Diam lama tanpa tuduhan", [], {**view, "now": 90.0}),
    ("Satu tuduhan AI + dua target ambigu", [demo_events[0], *ambiguous_events], view),
]:
    table, summary = build_features(scenario_events, scenario_view)
    selected, _ = choose_action(table, summary, scenario_view)
    scenario_results.append({"scenario": name, **selected})

display(pd.DataFrame(scenario_results))
"""
CHECKS = """# Pengujian kebijakan dan aliran informasi; bukan pengukuran win rate atau akurasi model.
checks = []
for text, intent, speaker, reply_to, expected in [
    ("Vote B", "offend", "A", None, ["B"]),
    ("Aku curiga B", "offend", "A", None, ["B"]),
    ("B bukan Hitman", "defend", "A", None, ["B"]),
    ("Aku bukan Hitman", "defend", "A", None, ["A"]),
    ("Vote aku", "offend", "A", None, ["A"]),
    ("Kamu Hitman", "offend", "A", None, []),
    ("Kamu Hitman", "offend", "A", "B", ["B"]),
    ("Dia Hitman", "offend", "A", "B", []),
    ("B kena Gag Order", "offend", "A", None, []),
    ("Jangan vote B", "offend", "A", None, []),
    ("Jangan vote B", "defend", "A", None, ["B"]),
    ("Kalau B Hitman, vote B", "offend", "A", None, []),
    ("Vote B, vote C", "offend", "A", None, ["B", "C"]),
    ("Kapan mulai?", "neutral", "A", None, []),
]:
    found, _ = extract_targets(text, intent, speaker, PLAYERS, reply_to)
    assert found == expected, (text, found, expected)
checks.append({"check": "14 kasus target, negasi, diri sendiri, reply-to", "result": "lulus"})

base_table, base_context = build_features(demo_events, view)
spam = [dict(demo_events[0], id=f"spam_{i}") for i in range(20)]
spam_table, _ = build_features([*demo_events, *spam, demo_events[0]], view)
assert base_table["accusers"].tolist() == spam_table["accusers"].tolist()
checks.append({"check": "Spam dan event duplikat tidak menambah jumlah penuduh", "result": "lulus"})

old_events = [dict(event, round=0) for event in demo_events]
old_table, _ = build_features(old_events, view)
assert old_table["accusers"].sum() == 0
low_table, _ = build_features([dict(event, confidence=0.1) for event in demo_events], view)
assert low_table["accusers"].sum() == 0
checks.append({"check": "Ronde lama dan confidence rendah tidak menjadi tuduhan", "result": "lulus"})

for changed_view in [{**view, "phase": "night"}, {**view, "phase": "tribunal"}, {**view, "can_chat": False}]:
    selected, _ = choose_action(base_table, base_context, changed_view)
    assert selected["action"] == "wait" and selected["intent"] is None
checks.append({"check": "Malam, tribunal, atau tanpa izin chat menghasilkan wait", "result": "lulus"})

hidden = [dict(event, role_asli="Hitman", hostage=True, gag_order=True) for event in demo_events]
hidden_table, hidden_context = build_features(hidden, {**view, "private_peek": {"B": "Hitman"}})
pd.testing.assert_frame_equal(hidden_table, base_table)
assert hidden_context == base_context
checks.append({"check": "Tambahan field rahasia tidak mengubah parameter", "result": "lulus"})

quiet_table, quiet_context = build_features([], {**view, "now": 90.0})
assert quiet_table["pressure"].sum() == 0
quiet_decision, _ = choose_action(quiet_table, quiet_context, {**view, "now": 90.0})
assert quiet_decision["intent"] == "neutral"
checks.append({"check": "Diam saja tidak menyebabkan offend", "result": "lulus"})

table, summary = build_features(demo_events[2:4], view)
selected, _ = choose_action(table, summary, view)
assert selected["intent"] == "offend" and selected["target"] == "D"
table, summary = build_features(demo_events[2:], view)
selected, _ = choose_action(table, summary, view)
assert selected["intent"] == "defend" and selected["target"] == "D"
checks.append({"check": "Tuduhan bersama dan konflik pembelaan memilih target D", "result": "lulus"})

display(pd.DataFrame(checks))
"""

def table(intro, rows):
    return intro + "\n\n| Nama variabel / proses | Untuk apa dan dari mana? | Arti nilai dan pengaruhnya |\n| --- | --- | --- |\n" + "\n".join(
        "| " + " | ".join(row) + " |" for row in rows
    )


def build(method):
    cells = []

    def md(text):
        cells.append(nbf.v4.new_markdown_cell(text))

    def code(text):
        ast.parse(text)
        cells.append(nbf.v4.new_code_cell(text.strip() + "\n"))

    title = "Utility AI" if method == "utility" else "Behavior Tree"
    md("# Civilian HOSTAGE — " + title)
    md("## Rencana dan Batas Sistem")
    md(
        "Notebook baru, mandiri, dan tidak mengimpor modul fuzzy atau menjalankan notebook training. "
        "Cakupan awal: memilih intent dan target chat Civilian. Keputusan vote dan skill tidak diterapkan. "
        "Zero Economy: tidak ada uang, budget, pembelian, atau tebusan.\n\n"
        "**Alur:** chat publik → NLU lokal → target berbasis aturan → parameter per ronde → "
        + title + " → instruksi untuk penulis percakapan. Tidak ada panggilan LLM/API di notebook ini. "
        "LLM kelak hanya menyusun kalimat dari keputusan yang sudah ditentukan.\n\n"
        "**Asumsi integrasi:** server mengirim ID pesan unik, ID pengirim, teks, nomor ronde, fase, "
        "waktu, awal fase siang, roster pemain yang diketahui masih hidup, serta izin bicara AI sendiri. "
        "Pemain yang disandera/dibungkam tetap berada dalam roster; jangan menyaring roster dari status "
        "korban yang tersembunyi. Reply-to opsional, kosong jika belum ada.\n\n"
        "**Pemilihan metode:** Utility AI mudah membandingkan beberapa tindakan dengan skor; Behavior Tree "
        "memudahkan pemeriksaan urutan alasan. Ini rekomendasi implementasi awal, belum klaim unggul secara empiris. "
        "Bayesian memerlukan model peluang pengamatan/role yang dapat dipertanggungjawabkan; RL memerlukan "
        "simulator dan eksperimen pertandingan, sehingga keduanya belum dipilih."
    )
    md("## Parameter yang Bisa dan Belum Bisa Digunakan")
    md(table("Parameter yang benar-benar dihitung dalam versi ini:", [
        ("Intent dan confidence", "Teks chat → model SVM/NB/IndoBERT tersimpan dari nlu_baru.", "Label offend/defend/neutral. Confidence 0–1 adalah keyakinan klasifikasi intent, bukan keyakinan bahwa tuduhan benar."),
        ("Target dan sumbernya", "Teks + daftar nama/ID publik + reply-to opsional → aturan ekstraksi.", "Nama/ID pemain. Kosong berarti neutral atau target belum diketahui, dibedakan lewat intent dan target_source."),
        ("accusers / defenders", "Kelompokkan chat bertarget menurut pengirim, intent, dan ronde.", "Jumlah pengirim berbeda, bukan jumlah pesan. Mereka belum tentu independen secara sosial atau berkata benar."),
        ("pressure / support", "Jumlah penuduh/pembela dibagi jumlah pemain lain yang dapat menjadi pengirim.", "0–1. AI dan target tidak menjadi sumber penguat. Nilai tinggi berarti tekanan/dukungan sosial, bukan peluang role."),
        ("silence", "Waktu sekarang dikurangi waktu chat terakhir pada siang ini, dibagi SILENCE_SECONDS.", "Dibatasi 0–1. Tidak bisa membedakan diam sukarela, Hostage, Gag Order, atau koneksi terputus. Hanya memicu ajakan bicara."),
        ("uncertainty", "Proporsi chat masuk yang confidence-nya rendah atau target non-neutral-nya tidak terselesaikan.", "0–1. Makin tinggi, makin masuk akal meminta klarifikasi."),
        ("few_messages", "Jumlah chat pemain lain pada ronde ini dibanding MIN_MESSAGES.", "Boolean; membantu Utility AI mengutamakan informasi saat pengamatan sedikit."),
        ("phase / can_chat", "Event fase publik dan izin aksi milik AI sendiri.", "Hanya day dengan can_chat=True boleh menghasilkan chat; kondisi lain wait."),
    ]))
    md(table("Kandidat berikut belum dihitung agar tidak mengarang data atau memakai informasi tersembunyi:", [
        ("Pergantian target tuduhan", "Urutan target dari pengirim yang sama per ronde.", "Dapat dihitung nanti, tetapi perubahan pendapat bukan otomatis kebohongan. Perlu benchmark target dahulu."),
        ("Vote, kesesuaian ucapan–vote", "Event voting yang memang dibuka kepada pemain.", "Belum jelas apakah pilihan per pemain terlihat. Jangan membaca vote privat atau memakai tidak-vote sebagai identitas korban."),
        ("Klaim role dan kontradiksi", "Ekstraksi klaim spesifik + riwayat, bukan classifier tiga intent.", "NLU saat ini tidak menghasilkan fakta klaim. Perlu anotasi dan extractor terpisah sebelum dipakai."),
        ("Hostage/Gag Order pada pemain lain", "Tidak ada sumber publik yang pasti sesuai Silent Terror.", "Jangan memasukkan status server tersembunyi. Rekap malam tanpa nama target tidak boleh diubah menjadi tuduhan pada nama tertentu."),
        ("Hasil Peek / Guard", "Informasi pribadi Stalker/Spy.", "Tidak tersedia bagi Civilian. Klaim chat tentang hasil skill masih merupakan ucapan yang belum terverifikasi."),
        ("Probabilitas Hitman", "Perlu model role dan evaluasi dari riwayat permainan berlabel.", "Tidak dihitung pada tahap ini. Skor tekanan maupun utility tidak boleh diberi nama probabilitas Hitman."),
    ]))
    md("## Library yang Digunakan")
    code(IMPORTS)
    md("## Konfigurasi dan Nilai Awal")
    md(table(
        "Angka berikut adalah keputusan desain untuk prototipe. Tidak berasal dari hasil NLU atau penelitian "
        "yang menetapkan ambang khusus HOSTAGE. Uji sensitivitas dan evaluasi pertandingan diperlukan sebelum mengklaim nilai terbaik.",
        [
            ("MIN_INTENT_CONFIDENCE = 0.60", "Menyaring prediksi intent sebelum menghitung tuduhan/pembelaan.", "0.60 berarti 60% confidence model. Lebih besar menyaring lebih banyak chat; threshold perlu dievaluasi untuk tiap backend."),
            ("MIN_ACCUSERS = 2", "Batas minimum pengirim berbeda untuk menantang pemain lain.", "Mengurangi pengaruh spam satu pengirim. Dua orang tetap bisa bersekongkol; ini bukan bukti kebenaran."),
            ("MIN_PRESSURE = 0.50", "Ambang tekanan sosial untuk tindakan challenge_player.", "Setengah sumber pengirim yang memenuhi syarat. Minimal dua penuduh tetap wajib."),
            ("SILENCE_SECONDS = 60", "Skala waktu diam selama siang.", "60 detik → silence=1. Lebih besar menunda ajakan bicara. Sesuaikan dengan panjang fase diskusi."),
            ("MIN_MESSAGES = 3", "Batas pengamatan sedikit untuk Utility AI.", "Kurang dari tiga chat menaikkan kebutuhan informasi. Behavior Tree memakai uncertainty dan cabang cadangan."),
            ("PLAYERS / AI_NAME", "Roster publik dan ID Civilian yang dikendalikan.", "Contoh enam pemain; ganti dengan data game. Jangan menghapus korban Hostage dari roster karena status itu rahasia."),
        ],
    ))
    code(CONFIG)
    md("## NLU Lokal dan Deteksi Target")
    md("### Prediksi Intent")
    md(
        "Antarmuka mengikuti nlu_baru: tiga label intent dan confidence. Di sini confidence dibawa dalam "
        "skala 0–1 (fungsi notebook NLU menampilkannya 0–100). Model dimuat sekali, bukan setiap chat.\n\n"
        "Default memakai intent_classifier_svm.pkl agar integrasi lokal langsung bisa dicoba. Untuk NB, "
        "ubah MODEL_FILENAME ke intent_classifier_nb.pkl atau varian tuning. Untuk IndoBERT, ubah "
        "NLU_BACKEND menjadi indobert; loader membaca folder model lokal dengan local_files_only=True "
        "dan berjalan di CPU. IndoBERT di sini adalah classifier intent, bukan LLM pengambil keputusan.\n\n"
        "Belum ada model prediksi target yang dilatih. Menambah kolom target pada dataset tidak otomatis "
        "mengubah classifier intent menjadi extractor target."
    )
    code(LOAD)
    code(PREDICT)
    md("### Target Tanpa LLM")
    md(table(
        "Resolver aturan ini mengutamakan target eksplisit dan boleh tidak menjawab. Reply-to harus "
        "diisi dari metadata server sebagai ID pengirim pesan yang dibalas; mention saja bukan bukti target.",
        [
            ("offend", "Cari pola tuduhan/vote terhadap nama pemain.", "Aku curiga B → B. B kena Gag Order → tidak diketahui, karena nama korban bukan otomatis penuduhan."),
            ("defend", "Cari pola pembelaan terhadap nama atau pembicara.", "B bukan Hitman → B. Aku bukan Hitman → ID pengirim."),
            ("diri_sendiri", "Kata aku/saya/gw pada posisi target dipetakan ke pengirim.", "Vote aku → pengirim. Aku curiga B → B, bukan pengirim. Mendukung offend dan defend."),
            ("kamu / lu", "Pola target orang kedua + reply_to.", "Kamu Hitman dengan reply_to=B → B. Tanpa metadata → tidak diketahui. Asumsi percakapan langsung ini tetap perlu diuji."),
            ("dia / mereka / multi-nama ambigu", "Belum ada resolusi acuan bahasa yang andal.", "Konservatif: tidak diketahui, bahkan sebagian kasus yang bisa dipahami manusia. Vote B, vote C bisa menghasilkan dua target."),
            ("neutral", "Tidak membuat relasi tuduhan/pembelaan.", "Daftar target input kosong. Tindakan neutral keluaran boleh punya penerima, misalnya mengajak B bicara; penerima itu bukan target tuduhan."),
        ],
    ))
    code(TARGET)
    md(
        "Keterbatasan penting: ini baseline aturan, bukan parser bahasa Indonesia lengkap. Sarkasme, "
        "typo, negasi kompleks, kutipan tidak bertanda, dan kalimat majemuk dapat gagal. "
        "Jangan melaporkan target accuracy dari contoh buatan saja. Pengembangan berikutnya yang disarankan "
        "adalah anotasi relasi (pengirim, intent, target/span), lalu bandingkan aturan dengan model "
        "token classification/relation classification lokal pada test terpisah; nama pemain perlu divariasikan "
        "agar model tidak sekadar menghafal A/B/C. Dataset target belum tersedia sebagai evaluasi di notebook ini."
    )
    md("### Mengubah Chat Menjadi Event")
    md("Input server hanya melewatkan field yang dipakai. Tidak ada pembacaan role asli atau penyebab pemain lain diam.")
    code(EVENT)
    md("## Perhitungan Parameter dan Izin Aksi")
    md(
        "Jalankan ulang build_features pada log observasi setiap kali perlu keputusan. Hanya ronde aktif dan "
        "pesan day sampai waktu sekarang yang dihitung. Event ID duplikat diabaikan. Spam dengan ID baru "
        "tetap hanya memberi satu hitungan penuduh/pembela per pengirim–target–intent.\n\n"
        "Pembelaan diri dan tuduhan diri tetap tercatat pada event, tetapi tidak dihitung sebagai "
        "dukungan/tuduhan eksternal. Chat AI sendiri tidak boleh memperkuat keputusannya. "
        "Roster tetap mencakup pemain diam: sistem tidak mengetahui siapa yang sebenarnya dibungkam.\n\n"
        "Akumulasi ini adalah hitungan pengamatan, bukan model perubahan keyakinan; tuduhan yang kemudian "
        "ditarik kembali masih tercatat sampai ronde berakhir. Jangan menyebutnya pendapat terkini."
    )
    code(FEATURES)
    code(GUARD)
    md("### Tampilan Laporan")
    md("Tanda — berarti kolom tidak berlaku, misalnya tidak ada target saat meminta informasi umum. Bukan skor nol atau nilai hasil yang diisi-isi.")
    code(REPORT)
    md("## Pengambilan Keputusan — " + title)
    if method == "utility":
        md(table("Setiap tindakan yang memenuhi syarat mendapat skor. Semua koefisien berikut adalah bobot awal yang dapat diubah.", [
            ("ask_*", "Meminta informasi; selalu menjadi kandidat.", "0.30 + 0.35 × uncertainty + 0.15 × few_messages. Bobot lebih besar membuat AI lebih sering meminta informasi."),
            ("self_*", "Membela diri saat ada penuduh eksternal.", "0.45 + 0.55 × pressure AI. Makin banyak tekanan, makin tinggi prioritas membela diri."),
            ("defend_*", "Membela pemain lain saat ada penuduh dan pembela.", "0.20 + 0.35 × pressure + 0.35 × support. Meminta proses yang adil, tidak menyatakan target pasti warga."),
            ("challenge_*", "Menantang target dengan ≥2 penuduh, pressure ≥0.50, tanpa pembela.", "0.25 + 0.60 × pressure. Ini reaksi sosial yang dapat ikut terseret tuduhan massal; perlu dievaluasi."),
            ("silence_*", "Mengajak pemain diam berbicara.", "0.20 + 0.25 × silence, hanya jika silence mencapai 1. Tidak menjadi komponen offend."),
            ("score / seri", "Mengurutkan pilihan.", "Skor terbesar dipilih. Seri mengikuti urutan kandidat tetap: informasi dahulu, kemudian pemain menurut ID. Skor bukan peluang kebenaran."),
        ]))
        code(UTILITY_CONFIG)
        code(UTILITY)
    else:
        md(
            "Bentuk pohon: **Selector** memilih **Sequence** pertama yang sukses. Setiap Sequence berisi "
            "satu pemeriksaan kondisi lalu satu aksi. Aksi dalam notebook selesai seketika sehingga cukup "
            "status success/failure; status running belum dibutuhkan untuk pergerakan/animasi.\n\n"
            "Izin chat diperiksa sebelum pohon. Urutan cabang: ketidakjelasan tinggi → pembelaan diri → "
            "pembelaan pemain yang diperdebatkan → tantangan pada pemain dengan tekanan tinggi → "
            "ajakan kepada pemain diam → permintaan informasi umum."
        )
        md(table("Berbeda dari Utility AI, cabang pertama yang lolos menang tanpa membandingkan skor semua tindakan.", [
            ("UNCERTAINTY_LIMIT = 0.50", "Ambang klarifikasi di cabang pertama.", "Jika ≥50% pengamatan tidak jelas, minta informasi dahulu. Lebih kecil membuat AI lebih sering berhenti untuk klarifikasi."),
            ("self_accused", "Minimal satu pemain lain menuduh AI.", "Membela diri bila cabang klarifikasi tidak aktif."),
            ("contested_player", "Target punya ≥1 penuduh dan ≥1 pembela.", "Pilih tekanan terbesar, lalu dukungan terbesar, lalu ID untuk seri. Dukungan bukan bukti role."),
            ("strong_pressure", "Syarat sama dengan kandidat challenge Utility AI.", "≥2 penuduh, pressure ≥0.50, tanpa pembela. Target menurut tekanan tertinggi lalu ID."),
            ("quiet_player / always", "Ajakan bicara lalu aksi cadangan.", "Diam tidak mengaktifkan tuduhan. always menjamin ada keluaran saat boleh chat."),
        ]))
        code(BT_CONFIG)
        code(BT)
    md("## Batas LLM untuk Percakapan")
    md(
        "Fungsi berikut hanya membuat payload, tidak mengirim apa pun. Di game, LLM boleh menulis kalimat "
        "sesuai action/intent/target yang sudah diputuskan. Payload juga memberikan batas fakta. "
        "Instruksi ini belum merupakan jaminan bahwa generator akan patuh; integrasi game tetap perlu "
        "memvalidasi keluaran atau memakai template cadangan. Fungsi prediksi NLU dan resolver target "
        "tidak mengandalkan API anotasi dataset."
    )
    code(HANDOFF)
    md("## Simulasi, Tabel Parameter, dan Keputusan")
    md("### Contoh dengan Intent yang Sudah Diketahui")
    md("Simulasi label tetap memisahkan pemeriksaan kebijakan dari kesalahan classifier. Tidak memakai role rahasia.")
    code(SIMULATION)
    code("""decision, trace = choose_action(features, context, view)
display(pd.DataFrame([decision]))
display(trace)
display(pd.DataFrame([prepare_nlg(decision)]))
""")
    md("### Beberapa Situasi Permainan")
    code(SCENARIOS)
    md("### Integrasi Model NLU yang Sudah Dilatih")
    md("Cell ini benar-benar membaca model lokal. Bandingkan label dan keputusan dengan simulasi sebelumnya; perbedaan prediksi model dapat mengubah keputusan. Tidak ada training ulang.")
    code(INTEGRATION)
    md("## Review dan Pengujian")
    md(
        "Checks berikut memeriksa konsistensi implementasi: target eksplisit, negasi, ketidakjelasan, "
        "batas ronde, spam, izin aksi, dan ketidakbergantungan pada field rahasia. "
        "Lulus checks bukan bukti bahwa strategi menang melawan manusia."
    )
    code(CHECKS)
    md("### Evaluasi yang Diperlukan Sebelum Dipakai sebagai Hasil Penelitian")
    md(
        "1. Anotasi manual target pada sampel chat nyata; ukur precision, recall, exact-match multi-target, "
        "serta proporsi tidak diketahui. Nilai salah target dan abstain harus dilaporkan terpisah.\n"
        "2. Bandingkan Utility AI, Behavior Tree, dan fuzzy pada skenario/event yang sama. "
        "Ukur salah tuduh warga, kemampuan membela diri, ketepatan target, latensi, dan kepatuhan izin chat.\n"
        "3. Setelah simulator tersedia, ukur win rate dan variasi antar-seed melawan beberapa strategi lawan. "
        "Pilih bobot/ambang di skenario pengembangan, bukan dari pertandingan test akhir.\n"
        "4. Uji penghapusan satu parameter (misalnya silence) dan perubahan ambang untuk mengetahui "
        "apakah parameter itu membantu. Dua penuduh berbeda tidak menjamin bukti independen.\n"
        "5. Penjadwal chat/cooldown perlu ditetapkan oleh game agar pemanggilan berulang tidak menghasilkan spam. "
        "Notebook memilih satu aksi per permintaan dan belum mengirim chat atau mengubah server game."
    )
    md("### Sumber Konsep dan Asal Angka")
    md(
        "Utility AI memakai penilaian kesesuaian relatif tindakan: "
        "[An Introduction to Utility Theory — Game AI Pro](https://www.gameaipro.com/GameAIPro/GameAIPro_Chapter09_An_Introduction_to_Utility_Theory.pdf).\n\n"
        "Behavior Tree mengorganisasikan pergantian tugas melalui komposisi seperti Selector dan Sequence: "
        "[Behavior Trees in Robotics and AI — Colledanchise dan Ögren](https://arxiv.org/abs/1709.00084).\n\n"
        "Sumber tersebut mendasari metode, **bukan angka ambang atau bukti bahwa tuduhan/diam menandakan Hitman**. "
        "Mekanik dan batas informasi berasal dari konsep HOSTAGE pengguna. Bobot, 60 detik, confidence 0.60, "
        "dan ambang 0.50 adalah rancangan awal yang transparan, belum dikalibrasi."
    )
    nb = nbf.v4.new_notebook(cells=cells)
    for cell in nb.cells:
        if cell.cell_type == "code" and "def show_table(" not in cell.source:
            cell.source = cell.source.replace("display(", "show_table(")
    nb.metadata = {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.11"},
    }
    nbf.validate(nb)
    return nb


if __name__ == "__main__":
    files = {
        "utility": OUT / "civilian_utility_ai.ipynb",
        "behavior_tree": OUT / "civilian_behavior_tree.ipynb",
    }
    for method, path in files.items():
        nb = build(method)
        nbf.write(nb, path)
        print(path.name, len(nb.cells), "cells")
