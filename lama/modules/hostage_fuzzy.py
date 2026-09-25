"""Fuzzy Logic bersama untuk menghitung indikasi bluff pada game HOSTAGE.

Semua parameter di bawah dapat diperoleh dari kejadian publik game. Modul ini
tidak membutuhkan `role_asli`, sehingga tidak membocorkan informasi rahasia.
"""

from __future__ import annotations

import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl


def _build_fuzzy_system() -> ctrl.ControlSystem:
    tuduhan = ctrl.Antecedent(np.arange(0, 11, 1), "tuduhan")
    kontradiksi = ctrl.Antecedent(np.arange(0, 11, 1), "kontradiksi")
    bukti = ctrl.Antecedent(np.arange(0, 11, 1), "bukti")
    keheningan = ctrl.Antecedent(np.arange(0, 11, 1), "keheningan")
    tekanan_vote = ctrl.Antecedent(np.arange(0, 11, 1), "tekanan_vote")
    indikasi_bluff = ctrl.Consequent(np.arange(0, 101, 1), "indikasi_bluff")

    for variable in (tuduhan, kontradiksi, bukti, keheningan, tekanan_vote):
        variable["rendah"] = fuzz.trimf(variable.universe, [0, 0, 4])
        variable["sedang"] = fuzz.trimf(variable.universe, [2, 5, 8])
        variable["tinggi"] = fuzz.trimf(variable.universe, [6, 10, 10])

    indikasi_bluff["rendah"] = fuzz.trimf(indikasi_bluff.universe, [0, 0, 40])
    indikasi_bluff["sedang"] = fuzz.trimf(indikasi_bluff.universe, [30, 50, 70])
    indikasi_bluff["tinggi"] = fuzz.trimf(indikasi_bluff.universe, [60, 100, 100])

    rules = [
        # Kontradiksi klaim adalah sinyal terkuat terhadap bluff.
        ctrl.Rule(kontradiksi["tinggi"], indikasi_bluff["tinggi"]),
        ctrl.Rule(kontradiksi["sedang"], indikasi_bluff["sedang"]),

        # Bukti publik kuat + tekanan tuduhan yang tinggi memperbesar kecurigaan.
        ctrl.Rule(bukti["tinggi"] & tuduhan["tinggi"], indikasi_bluff["tinggi"]),
        ctrl.Rule(bukti["tinggi"] & kontradiksi["sedang"], indikasi_bluff["tinggi"]),
        ctrl.Rule(bukti["tinggi"] & tuduhan["sedang"], indikasi_bluff["sedang"]),
        ctrl.Rule(bukti["tinggi"] & tuduhan["rendah"], indikasi_bluff["sedang"]),

        # Banyak tuduhan tanpa bukti tetap dicurigai, tetapi tidak langsung tinggi.
        ctrl.Rule(tuduhan["tinggi"] & bukti["rendah"], indikasi_bluff["sedang"]),
        ctrl.Rule(tuduhan["tinggi"] & bukti["sedang"], indikasi_bluff["sedang"]),
        ctrl.Rule(tuduhan["sedang"] & bukti["sedang"], indikasi_bluff["sedang"]),

        # Silent Terror hanya sinyal tambahan: diam tidak pernah cukup untuk
        # menuduh seseorang tanpa kontradiksi atau bukti publik lain.
        ctrl.Rule(keheningan["tinggi"] & kontradiksi["sedang"], indikasi_bluff["tinggi"]),
        ctrl.Rule(keheningan["tinggi"] & kontradiksi["rendah"], indikasi_bluff["rendah"]),

        # Lonjakan voting menjadi kuat hanya jika didukung bukti/kontradiksi.
        ctrl.Rule(tekanan_vote["tinggi"] & bukti["tinggi"], indikasi_bluff["tinggi"]),
        ctrl.Rule(tekanan_vote["tinggi"] & kontradiksi["sedang"], indikasi_bluff["tinggi"]),
        ctrl.Rule(tekanan_vote["tinggi"] & bukti["rendah"], indikasi_bluff["sedang"]),

        # Klaim konsisten dengan bukti lemah cenderung merupakan pembelaan biasa.
        ctrl.Rule(kontradiksi["rendah"] & bukti["rendah"] & tuduhan["rendah"], indikasi_bluff["rendah"]),
        ctrl.Rule(kontradiksi["rendah"] & bukti["rendah"] & tuduhan["sedang"], indikasi_bluff["rendah"]),
        ctrl.Rule(kontradiksi["rendah"] & bukti["sedang"] & tuduhan["rendah"], indikasi_bluff["rendah"]),
    ]
    return ctrl.ControlSystem(rules)


_FUZZY_SYSTEM = _build_fuzzy_system()


def _clamp_score(value: float) -> float:
    """Membatasi nilai masukan ke skala publik 0--10."""
    return float(np.clip(float(value), 0, 10))


def calculate_bluff_indicator(
    accusation_count: float,
    claim_contradiction: float,
    public_evidence: float,
    silence_anomaly: float = 0,
    vote_pressure: float = 0,
) -> float:
    """Mengembalikan indikasi bluff 0--100 berdasarkan data publik.

    Args:
        accusation_count: Intensitas tuduhan terhadap pemain pada skala 0--10.
        claim_contradiction: Seberapa sering klaim/alibi pemain bertentangan,
            pada skala 0--10.
        public_evidence: Kekuatan bukti yang terlihat semua pemain, misalnya
            pola voting, Gag Order, atau hasil kejadian malam, pada skala 0--10.
        silence_anomaly: Kejanggalan pemain yang tiba-tiba diam pada skala 0--10.
            Ini hanya penguat, bukan bukti bahwa pemain pasti terkena Hostage.
        vote_pressure: Tekanan vote yang mengarah kepada pemain pada skala 0--10.
    """
    simulation = ctrl.ControlSystemSimulation(_FUZZY_SYSTEM)
    simulation.input["tuduhan"] = _clamp_score(accusation_count)
    simulation.input["kontradiksi"] = _clamp_score(claim_contradiction)
    simulation.input["bukti"] = _clamp_score(public_evidence)
    simulation.input["keheningan"] = _clamp_score(silence_anomaly)
    simulation.input["tekanan_vote"] = _clamp_score(vote_pressure)
    simulation.compute()
    return float(simulation.output["indikasi_bluff"])


def describe_bluff_level(bluff_indicator: float) -> str:
    """Mengubah skor 0--100 menjadi label yang mudah ditampilkan ke pemain."""
    score = float(np.clip(float(bluff_indicator), 0, 100))
    if score < 40:
        return "rendah"
    if score < 70:
        return "sedang"
    return "tinggi"
