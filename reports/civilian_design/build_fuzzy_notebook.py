"""Membuat notebook fuzzy mandiri; tidak menulis ulang dua notebook pembanding."""

import ast
import copy
from pathlib import Path

import nbformat as nbf

from build_notebooks import table


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "ai_2_dataset_baru/civilian_fuzzy.ipynb"

CONFIG = """# Kurva saling bertumpang tindih; high memakai plateau mulai 0.5.
INPUT_MEMBERSHIP = {
    "low": [0.0, 0.0, 0.5],
    "medium": [0.0, 0.5, 1.0],
    "high": [0.0, 0.5, 1.0, 1.0],
}

# Kurva output prioritas 0-100; bukan persentase probabilitas.
OUTPUT_MEMBERSHIP = {
    "low": [0.0, 0.0, 50.0],
    "medium": [0.0, 50.0, 100.0],
    "high": [50.0, 100.0, 100.0],
}

# Setiap matriks: baris = input pertama low/medium/high, kolom = input kedua.
# Isinya kelompok prioritas keluaran. Semua 3 x 3 pasangan memiliki aturan.
FUZZY_RULES = {
    "ask_information": {
        "inputs": ("uncertainty", "few_messages"),
        "matrix": [
            ["low", "medium", "medium"],
            ["medium", "high", "high"],
            ["high", "high", "high"],
        ],
    },
    "defend_self": {
        "inputs": ("pressure", "uncertainty"),
        "matrix": [
            ["medium", "medium", "low"],
            ["high", "high", "medium"],
            ["high", "high", "medium"],
        ],
    },
    "defend_player": {
        "inputs": ("pressure", "support"),
        "matrix": [
            ["low", "medium", "medium"],
            ["medium", "high", "high"],
            ["medium", "high", "high"],
        ],
    },
    "challenge_player": {
        "inputs": ("pressure", "uncertainty"),
        "matrix": [
            ["low", "low", "low"],
            ["high", "medium", "low"],
            ["high", "medium", "low"],
        ],
    },
    "ask_quiet_player": {
        "inputs": ("silence", "uncertainty"),
        "matrix": [
            ["low", "low", "low"],
            ["medium", "medium", "medium"],
            ["high", "high", "medium"],
        ],
    },
}
"""

BUILD = """# Membuat satu sistem Mamdani untuk tiap tindakan dengan sembilan aturan lengkap.
def build_fuzzy_systems():
    systems = {}
    terms = list(INPUT_MEMBERSHIP)
    for action, specification in FUZZY_RULES.items():
        first_name, second_name = specification["inputs"]
        first = ctrl.Antecedent(np.linspace(0, 1, 101), first_name)
        second = ctrl.Antecedent(np.linspace(0, 1, 101), second_name)
        priority = ctrl.Consequent(np.linspace(0, 100, 101), "priority")
        priority.defuzzify_method = "centroid"

        for name, points in INPUT_MEMBERSHIP.items():
            membership = fuzz.trapmf if len(points) == 4 else fuzz.trimf
            first[name] = membership(first.universe, points)
            second[name] = membership(second.universe, points)
        for name, points in OUTPUT_MEMBERSHIP.items():
            priority[name] = fuzz.trimf(priority.universe, points)

        rules = []
        for i, first_term in enumerate(terms):
            for j, second_term in enumerate(terms):
                output_term = specification["matrix"][i][j]
                rules.append(ctrl.Rule(
                    first[first_term] & second[second_term], priority[output_term],
                    label=f"{action}:{first_term}+{second_term}->{output_term}",
                ))
        systems[action] = ctrl.ControlSystem(rules)
    return systems
"""

EVALUATE = """# Menghitung prioritas dan menampilkan aturan aktif beserta kekuatan aktivasinya.
def evaluate_fuzzy(action, inputs):
    specification = FUZZY_RULES[action]
    names = specification["inputs"]
    values = {name: float(inputs[name]) for name in names}
    if any(not math.isfinite(value) or not 0 <= value <= 1 for value in values.values()):
        raise ValueError("Input fuzzy harus angka hingga dalam rentang 0-1.")

    simulation = FUZZY_SIMULATIONS[action]
    simulation.inputs(values)
    simulation.compute()
    score = float(simulation.output["priority"])

    terms = list(INPUT_MEMBERSHIP)
    first, second = list(FUZZY_SYSTEMS[action].antecedents)
    variables = {first.label: first, second.label: second}
    active_rules = []
    for i, first_term in enumerate(terms):
        first_strength = fuzz.interp_membership(
            variables[names[0]].universe, variables[names[0]][first_term].mf, values[names[0]],
        )
        for j, second_term in enumerate(terms):
            second_strength = fuzz.interp_membership(
                variables[names[1]].universe, variables[names[1]][second_term].mf, values[names[1]],
            )
            strength = min(first_strength, second_strength)
            if strength > 0:
                active_rules.append({
                    "input_1": f"{names[0]}={first_term}",
                    "input_2": f"{names[1]}={second_term}",
                    "output": specification["matrix"][i][j],
                    "activation": float(strength),
                })
    return score, pd.DataFrame(active_rules)
"""

DECIDE = """# Menilai tindakan yang layak lewat fuzzy, lalu memilih prioritas terbesar.
def choose_action(features, context, view):
    blocked = chat_permission(view)
    if blocked is not None:
        return blocked, pd.DataFrame([blocked])

    # Syarat kelayakan mencegah output fuzzy rendah menjadi tuduhan tanpa bukti pengamatan.
    candidates = [{
        "action": "ask_information", "intent": "neutral", "target": None,
        "inputs": {
            "uncertainty": context["uncertainty"],
            "few_messages": float(context["few_messages"]),
        },
        "reason": "Meminta informasi berdasarkan ketidakjelasan target/intent dan jumlah chat.",
    }]
    for row in features.sort_values("player").to_dict("records"):
        player = row["player"]
        if player == view["ai"]:
            if row["accusers"] > 0:
                candidates.append({
                    "action": "defend_self", "intent": "defend", "target": player,
                    "inputs": {"pressure": row["pressure"], "uncertainty": context["uncertainty"]},
                    "reason": f'{row["accusers"]} pemain berbeda menuduh AI dalam ronde ini.',
                })
            continue

        if row["accusers"] > 0 and row["defenders"] > 0:
            candidates.append({
                "action": "defend_player", "intent": "defend", "target": player,
                "inputs": {"pressure": row["pressure"], "support": row["support"]},
                "reason": f'{player} menerima tuduhan dan pembelaan; minta penilaian adil, bukan memastikan role.',
            })

        if (row["accusers"] >= MIN_ACCUSERS and row["pressure"] >= MIN_PRESSURE
                and row["defenders"] == 0):
            candidates.append({
                "action": "challenge_player", "intent": "offend", "target": player,
                "inputs": {"pressure": row["pressure"], "uncertainty": context["uncertainty"]},
                "reason": f'{player} dituduh {row["accusers"]} pemain berbeda; ini dugaan sosial, belum bukti Hitman.',
            })

        # silence tidak pernah masuk ke sistem fuzzy challenge_player.
        if row["silence"] >= 1.0:
            candidates.append({
                "action": "ask_quiet_player", "intent": "neutral", "target": player,
                "inputs": {"silence": row["silence"], "uncertainty": context["uncertainty"]},
                "reason": f'{player} belum chat minimal {SILENCE_SECONDS:g} detik siang; penyebab tidak diketahui.',
            })

    for candidate in candidates:
        candidate["score"], candidate["active_rules"] = evaluate_fuzzy(
            candidate["action"], candidate["inputs"],
        )

    # Nilai seri mengikuti urutan tetap: informasi dahulu, kemudian ID pemain.
    ranked = sorted(candidates, key=lambda item: round(item["score"], 10), reverse=True)
    winner = ranked[0]
    decision = {name: winner[name] for name in ("action", "intent", "target", "reason")}
    trace = pd.DataFrame([{
        "action": item["action"], "intent": item["intent"], "target": item["target"],
        "score": item["score"], "inputs": str(item["inputs"]),
        "active_rules": len(item["active_rules"]),
    } for item in ranked])
    return decision, trace
"""

BOUNDARY = """# Mencoba seluruh kombinasi grid termasuk 0, tepat 0.5, dan 1.
# Kelengkapan aturan memastikan tidak ada lubang pada batas seperti desain lama.
coverage_rows = []
for action, specification in FUZZY_RULES.items():
    scores = []
    for first_value in np.linspace(0, 1, 11):
        for second_value in np.linspace(0, 1, 11):
            score, rules = evaluate_fuzzy(action, dict(zip(
                specification["inputs"], [first_value, second_value],
            )))
            assert math.isfinite(score) and 0 <= score <= 100 and not rules.empty
            scores.append(score)
    coverage_rows.append({
        "action": action, "combinations": len(scores),
        "min_priority": min(scores), "max_priority": max(scores), "result": "lulus",
    })
show_table(pd.DataFrame(coverage_rows))

# Input eksternal yang tidak valid harus dihentikan, bukan menghasilkan prioritas palsu.
for invalid in [float("nan"), float("inf"), -0.1, 1.1]:
    try:
        evaluate_fuzzy("defend_self", {"pressure": invalid, "uncertainty": 0.0})
    except ValueError:
        pass
    else:
        raise AssertionError("Input fuzzy tidak valid diterima.")

# Pada ketidakjelasan tetap nol, menambah tekanan tidak boleh menurunkan prioritas pembelaan.
self_curve = [
    evaluate_fuzzy("defend_self", {"pressure": p, "uncertainty": 0.0})[0]
    for p in np.linspace(0, 1, 21)
]
assert np.all(np.diff(self_curve) >= -1e-8)
print("605 kombinasi input tercakup; input tidak valid ditolak; kurva pembelaan diperiksa.")
"""

PLOT = """# Memvisualisasikan overlap; di x=0.5, medium dan high sama-sama aktif penuh.
fig, axes = plt.subplots(1, 2, figsize=(11, 3.5))
for axis, membership, upper, title in [
    (axes[0], INPUT_MEMBERSHIP, 1, "Input membership (0-1)"),
    (axes[1], OUTPUT_MEMBERSHIP, 100, "Output priority membership (0-100)"),
]:
    universe = np.linspace(0, upper, 201)
    for name, points in membership.items():
        membership_function = fuzz.trapmf if len(points) == 4 else fuzz.trimf
        axis.plot(universe, membership_function(universe, points), label=name, linewidth=2)
    axis.set(title=title, xlabel="Value", ylabel="Membership degree", ylim=(-0.02, 1.05))
    axis.grid(alpha=0.25)
    axis.legend()
fig.tight_layout()
plt.show()
"""

def main():
    source = ROOT / "ai_2_dataset_baru/civilian_utility_ai.ipynb"
    nb = nbf.read(source, as_version=4)
    start = next(i for i, c in enumerate(nb.cells) if c.source.startswith("## Pengambilan Keputusan"))
    end = next(i for i, c in enumerate(nb.cells) if c.source == "## Batas LLM untuk Percakapan")
    additions = []

    def md(text):
        additions.append(nbf.v4.new_markdown_cell(text))

    def code(text):
        ast.parse(text)
        additions.append(nbf.v4.new_code_cell(text.strip() + "\n"))

    md("## Pengambilan Keputusan — Fuzzy Mamdani")
    md(
        "Fuzzy baru memiliki lima sistem kecil, masing-masing dua input dan satu output prioritas. "
        "Setiap sistem punya sembilan aturan lengkap. Intent tidak lagi ditentukan dari satu skor tunggal "
        "dengan batas 35/65. Sistem membandingkan prioritas tindakan yang memenuhi syarat.\n\n"
        "Mamdani: ubah input menjadi derajat keanggotaan → aktifkan aturan dengan AND/minimum → "
        "gabungkan output dengan maksimum → hitung centroid (titik berat area) → pilih kandidat berprioritas terbesar. "
        "Kesamaan skala output memudahkan perbandingan tindakan, tetapi keseimbangan aturan antar-tindakan "
        "tetap perlu diuji. Ini rancangan kebijakan awal, bukan hasil optimasi."
    )
    md("### Input, Output, dan Asal Angka")
    md(table("Seluruh input berasal dari parameter publik yang dihitung di atas.", [
        ("defend_self", "pressure pada AI + uncertainty", "Tekanan meningkat → prioritas membela diri naik. Ketidakjelasan tinggi dapat menurunkannya."),
        ("defend_player", "pressure + support pada pemain lain", "Tuduhan dan dukungan bersamaan memicu pembelaan yang meminta penilaian adil; dukungan tidak membuktikan warga."),
        ("challenge_player", "pressure target + uncertainty", "Tekanan tinggi dapat menaikkan prioritas menantang; ketidakjelasan menurunkannya. Silence tidak menjadi input."),
        ("ask_information", "uncertainty + few_messages", "Ketidakjelasan atau sedikit chat meningkatkan kebutuhan informasi. few_messages dibawa sebagai 0/1."),
        ("ask_quiet_player", "silence + uncertainty", "Diam lama memicu ajakan bicara. Tidak mengidentifikasi korban atau role."),
        ("INPUT_MEMBERSHIP", "Dua segitiga dan satu trapesium pada rentang 0–1", "low=[0,0,0.5], medium=[0,0.5,1], high=[0,0.5,1,1]. Segitiga: kiri/puncak/kanan. Trapesium: kiri/awal plateau/akhir plateau/kanan. Plateau high mencegah penurunan aktivasi saat pressure bertambah di atas 0.5."),
        ("OUTPUT_MEMBERSHIP", "Tiga segitiga pada rentang prioritas 0–100", "low=[0,0,50], medium=[0,50,100], high=[50,100,100]. Centroid murni low sekitar 16.67, medium 50, high 83.33; tidak harus mencapai 0 atau 100."),
        ("FUZZY_RULES", "Matriks aturan pilihan perancang", "Baris input pertama dan kolom input kedua berurutan low/medium/high. Nilai matriks adalah kategori prioritas."),
    ]))
    code(CONFIG)
    md("### Membaca Aturan")
    md(
        "Tiap tabel berikut berisi sembilan aturan. Contoh defend_self: baris pressure=medium dan "
        "kolom uncertainty=low menghasilkan prioritas high. Tidak ada pasangan input yang dibiarkan tanpa aturan."
    )
    code("""for action, specification in FUZZY_RULES.items():
    first_name, second_name = specification["inputs"]
    print(f"{action} | baris: {first_name}, kolom: {second_name}")
    rule_table = pd.DataFrame(
        specification["matrix"], index=list(INPUT_MEMBERSHIP), columns=list(INPUT_MEMBERSHIP),
    ).rename_axis(first_name).reset_index()
    show_table(rule_table)
""")
    md("### Pembentukan Sistem dan Kurva Keanggotaan")
    code(BUILD)
    code("""# Sistem dibuat sekali; simulasi dipakai kembali untuk keputusan berikutnya.
FUZZY_SYSTEMS = build_fuzzy_systems()
FUZZY_SIMULATIONS = {
    action: ctrl.ControlSystemSimulation(system, flush_after_run=2048)
    for action, system in FUZZY_SYSTEMS.items()
}
""")
    code(PLOT)
    md("### Inferensi dan Pemilihan Tindakan")
    md(
        "Syarat kelayakan sama dengan notebook pembanding: membela diri hanya saat ada tuduhan; "
        "membela orang lain saat ada penuduh dan pembela; menantang target perlu minimal dua penuduh berbeda, "
        "pressure ≥0.50, dan belum ada pembela; mengajak pemain diam perlu silence=1. "
        "Meminta informasi selalu tersedia. Syarat ini mencegah skor centroid rendah tetap menghasilkan "
        "tuduhan saat tidak ada pengamatan. Pengirim berbeda bukan bukti independen atau benar.\n\n"
        "Aturan dan kurva dapat diubah di cell konfigurasi, kemudian jalankan kembali cell pembentukan "
        "sistem. Tidak perlu training NLU ulang."
    )
    code(EVALUATE)
    code(DECIDE)
    nb.cells[start:end] = additions
    for c in nb.cells:
        if c.cell_type == "code":
            c.outputs = []
            c.execution_count = None
            if c.source.startswith("from pathlib import Path"):
                c.source += "\nimport skfuzzy as fuzz\nfrom skfuzzy import control as ctrl\nimport matplotlib.pyplot as plt\n"
        else:
            if c.source.startswith("# Civilian HOSTAGE"):
                c.source = "# Civilian HOSTAGE — Fuzzy Mamdani"
            if c.source.startswith("Notebook baru, mandiri"):
                c.source = (
                    "Notebook fuzzy baru dan mandiri; fuzzy lama, Utility AI, Behavior Tree, dan NLU tidak diubah. "
                    "Cakupan awal: intent dan target chat Civilian. Tidak mengatur vote atau skill. "
                    "Tidak ada uang, budget, pembelian, atau tebusan.\n\n"
                    "**Alur:** chat publik → NLU lokal → target dengan aturan tanpa LLM → parameter per ronde "
                    "→ inferensi fuzzy → keputusan → instruksi untuk penyusun percakapan. "
                    "Tidak ada pemanggilan LLM/API di notebook ini; LLM kelak hanya menulis percakapan.\n\n"
                    "**Asumsi event:** ID pesan, pengirim, teks, ronde, fase, waktu, awal siang, roster publik, "
                    "dan izin chat AI sendiri tersedia. Reply-to opsional. Roster tetap mencakup pemain "
                    "Hostage/Gag Order; status tersembunyi mereka tidak dipakai untuk menyaring roster.\n\n"
                    "**Perbaikan dari fuzzy lama:** parameter tidak hanya persentase tuduhan; tuduhan dibatasi per ronde "
                    "dan pengirim; keputusan terpisah untuk beberapa tindakan; uncertainty ikut dipertimbangkan; "
                    "seluruh rentang keanggotaan tercakup termasuk tepat 50%; ada trace dan pengujian."
                )
            c.source = c.source.replace("batas pengamatan sedikit untuk Utility AI", "batas pengamatan sedikit untuk fuzzy")
            c.source = c.source.replace("Batas pengamatan sedikit untuk Utility AI.", "Batas pengamatan sedikit untuk fuzzy.")
            c.source = c.source.replace("membantu Utility AI", "membantu fuzzy")
            c.source = c.source.replace("Behavior Tree memakai uncertainty dan cabang cadangan.", "Input ini masuk ke sistem ask_information sebagai 0 atau 1.")
    simulation_index = next(i for i, c in enumerate(nb.cells) if c.cell_type == "code" and c.source.startswith("decision, trace ="))
    nb.cells[simulation_index + 1:simulation_index + 1] = [
        nbf.v4.new_markdown_cell("### Alasan Fuzzy untuk Tindakan Terpilih"),
        nbf.v4.new_markdown_cell(
            "Activation adalah derajat aktif aturan (0–1), bukan confidence NLU atau peluang Hitman. "
            "Skor final berasal dari centroid gabungan output aturan, bukan rata-rata sederhana activation."
        ),
        nbf.v4.new_code_cell("""# Memperlihatkan aturan aktif pada keputusan contoh.
if decision["action"] != "wait":
    selected_row = features.set_index("player")
    selected_inputs = {
        "uncertainty": context["uncertainty"], "few_messages": float(context["few_messages"]),
    }
    if decision["target"] is not None:
        selected_inputs.update(selected_row.loc[decision["target"]].to_dict())
    selected_score, active_rules = evaluate_fuzzy(decision["action"], selected_inputs)
    print(f"Prioritas fuzzy: {selected_score:.3f}")
    show_table(active_rules)
"""),
    ]
    index = next(i for i, c in enumerate(nb.cells) if c.source.startswith("### Evaluasi yang Diperlukan"))
    nb.cells[index:index] = [
        nbf.v4.new_markdown_cell("### Pengujian Cakupan dan Batas Fuzzy"),
        nbf.v4.new_markdown_cell(
            "Grid 11×11 untuk setiap tindakan mencakup 0, 0.5, dan 1. "
            "Tes memeriksa output hingga, aturan aktif, rentang nilai, serta arah kurva pembelaan diri. "
            "Ini verifikasi numerik dan perilaku rancangan, bukan evaluasi strategi pertandingan."
        ),
        nbf.v4.new_code_cell(BOUNDARY),
    ]
    nb.cells[-1].source = (
        "Implementasi Mamdani, membership function, ControlSystemSimulation, dan defuzzifikasi mengikuti "
        "[dokumentasi resmi scikit-fuzzy](https://scikit-fuzzy.readthedocs.io/en/latest/auto_examples/plot_tipping_problem_newapi.html). "
        "Pemeriksaan grid input mengikuti gagasan evaluasi ruang kontrol pada "
        "[contoh lanjutan resmi](https://scikit-fuzzy.readthedocs.io/en/latest/auto_examples/plot_control_system_advanced.html).\n\n"
        "**Sumber tersebut menjelaskan metode, bukan parameter khusus HOSTAGE.** "
        "Mekanik dan batas informasi berasal dari konsep game pengguna. Titik kurva, isi matriks, "
        "confidence 0.60, dua penuduh, ambang tekanan 0.50, dan 60 detik adalah rancangan awal. "
        "Angka perlu dituning pada skenario pengembangan lalu diuji terpisah; bukan diklaim sebagai standar ilmiah.\n\n"
        "Perbandingan adil dengan Utility AI/Behavior Tree memerlukan event, NLU, target, dan "
        "batas informasi yang sama. Prioritas fuzzy bukan probabilitas Hitman atau kebenaran tuduhan."
    )
    for c in nb.cells:
        if c.cell_type == "code":
            ast.parse(c.source)
    nbf.validate(nb)
    nbf.write(nb, OUT)
    print(OUT.name, len(nb.cells), "cells")


if __name__ == "__main__":
    main()
