"""Fuzzy Logic bersama untuk menghitung indikasi bluff pada game HOSTAGE.

Semua parameter di bawah dapat diperoleh dari kejadian publik game. Modul ini
tidak membutuhkan `role_asli`, sehingga tidak membocorkan informasi rahasia.

Skema intent yang dipakai di seluruh modul ini: "offend", "defend", "neutral"
(hasil dari NLU intent classifier 3-kelas).
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field

import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

# Kedua label lama (defending & bluffing) sekarang melebur jadi satu kelas
# "defend" di classifier 3-kelas, begitu juga accusing/redirecting/deflecting
# melebur jadi "offend". Konstanta ini disamakan ke skema baru.
DEFENSIVE_INTENTS = {"defend"}
ACCUSATION_INTENTS = {"offend"}


@dataclass
class PlayerChatLog:
    """Menyimpan riwayat chat dan sinyal publik untuk satu pemain, dari sudut pandang Civilian."""

    chats: list[str] = field(default_factory=list)
    jumlah_menuduh: int = 0          # berapa kali PEMAIN INI dapat intent offend
    jumlah_bela_diri: int = 0        # berapa kali PEMAIN INI dapat intent defend
    giliran_diam_berturut: int = 0

    def catat_chat(self, teks: str, intent: str) -> None:
        """Tambahkan satu chat baru dari pemain ini dan perbarui counter berdasarkan intent-nya."""
        self.chats.append(teks)
        self.giliran_diam_berturut = 0  # baru saja chat, reset hitungan diam
        if intent in ACCUSATION_INTENTS:
            self.jumlah_menuduh += 1
        if intent in DEFENSIVE_INTENTS:
            self.jumlah_bela_diri += 1

    def catat_diam(self) -> None:
        """Panggil sekali per giliran chat ketika pemain ini tidak chat sama sekali."""
        self.giliran_diam_berturut += 1


class CivilianSuspicionTracker:
    """Menyimpan PlayerChatLog untuk setiap pemain yang dipantau seorang Civilian."""

    def __init__(self) -> None:
        self._logs: dict[str, PlayerChatLog] = defaultdict(PlayerChatLog)

    def catat_chat(self, pemain: str, teks: str, intent: str) -> None:
        """pemain = orang yang MENGUCAPKAN chat ini (bukan yang dituduh)."""
        self._logs[pemain].catat_chat(teks, intent)

    def catat_diam(self, pemain: str) -> None:
        self._logs[pemain].catat_diam()

    def get_log(self, pemain: str) -> PlayerChatLog:
        return self._logs[pemain]


# ---------------------------------------------------------------------------
# Fuzzy system: seberapa besar AI harus condong ke defend/offend/neutral,
# berdasarkan persentase pemain yang menuduh AI.
#
# Aturan dasar (gradasi fuzzy dari threshold tegas):
#   1. Dituduh oleh >=50% jumlah pemain -> defend
#   2. Dituduh oleh <50% (tapi >0%) jumlah pemain -> offend
#   3. Tidak ada yang menuduh sama sekali -> neutral
# ---------------------------------------------------------------------------

def _build_ai_defense_fuzzy_system() -> ctrl.ControlSystem:
    persentase_dituduh = ctrl.Antecedent(np.arange(0, 101, 1), "persentase_dituduh")
    kecenderungan_intent = ctrl.Consequent(np.arange(0, 101, 1), "kecenderungan_intent")

    # Tiga zona kasar: nyaris tidak ada yang menuduh, sebagian kecil, mayoritas.
    persentase_dituduh["nihil"] = fuzz.trimf(persentase_dituduh.universe, [0, 0, 1])
    persentase_dituduh["minoritas"] = fuzz.trimf(persentase_dituduh.universe, [0, 25, 50])
    persentase_dituduh["mayoritas"] = fuzz.trimf(persentase_dituduh.universe, [50, 100, 100])

    # Skor rendah -> neutral, tengah -> offend, tinggi -> defend.
    kecenderungan_intent["netral"] = fuzz.trimf(kecenderungan_intent.universe, [0, 0, 30])
    kecenderungan_intent["offend"] = fuzz.trimf(kecenderungan_intent.universe, [20, 50, 80])
    kecenderungan_intent["defend"] = fuzz.trimf(kecenderungan_intent.universe, [70, 100, 100])

    rules = [
        ctrl.Rule(persentase_dituduh["nihil"], kecenderungan_intent["netral"]),
        ctrl.Rule(persentase_dituduh["minoritas"], kecenderungan_intent["offend"]),
        ctrl.Rule(persentase_dituduh["mayoritas"], kecenderungan_intent["defend"]),
    ]
    return ctrl.ControlSystem(rules)


_AI_DEFENSE_FUZZY_SYSTEM = _build_ai_defense_fuzzy_system()


def calculate_ai_defense_score(persentase_dituduh: float) -> float:
    """0-100: makin tinggi skor, makin condong AI harus defend (bukan offend/neutral)."""
    simulation = ctrl.ControlSystemSimulation(_AI_DEFENSE_FUZZY_SYSTEM)
    simulation.input["persentase_dituduh"] = float(np.clip(persentase_dituduh, 0, 100))
    simulation.compute()
    return float(simulation.output["kecenderungan_intent"])


def describe_ai_defense_intent(score: float) -> str:
    """Ubah skor 0-100 jadi label intent AI."""
    score = float(np.clip(score, 0, 100))
    if score < 35:
        return "neutral"
    if score < 65:
        return "offend"
    return "defend"


NAMA_AI_DEFAULT = "AI"


@dataclass
class AISelfDefenseState:
    """Melacak tuduhan yang mengarah ke AI, untuk menentukan intent balasan AI.

    - persentase_dituduh: persentase pemain (dari total pemain) yang sudah
      pernah menuduh AI secara langsung.
    - jumlah_menuduh_global: berapa kali PEMAIN LAIN menuduh PEMAIN LAIN
      (bukan menuduh AI) -- dipakai sebagai sinyal tambahan/konteks, bukan
      untuk menentukan intent AI sendiri.
    """

    total_pemain: int
    nama_ai: str = NAMA_AI_DEFAULT
    pemain_penuduh_ai: set[str] = field(default_factory=set)
    jumlah_menuduh_global: int = 0

    def catat_chat(self, pemain: str, intent: str, target: str | None = None) -> None:
        """pemain = siapa yang bicara. target = siapa yang dituduh (hanya relevan kalau intent == 'offend').

        Kalau target == nama AI, dicatat sebagai tuduhan terhadap AI.
        Kalau target pemain lain (bukan AI), dihitung ke jumlah_menuduh_global.
        """
        if intent != "offend" or target is None:
            return
        if target == self.nama_ai:
            self.pemain_penuduh_ai.add(pemain)
        else:
            self.jumlah_menuduh_global += 1

    @property
    def persentase_dituduh(self) -> float:
        """Persentase pemain (dari total pemain) yang sudah menuduh AI."""
        if self.total_pemain <= 0:
            return 0.0
        return len(self.pemain_penuduh_ai) / self.total_pemain * 100

    def rekomendasi_intent_ai(self) -> str:
        """Label intent AI (neutral/offend/defend) berdasarkan fuzzy score."""
        score = calculate_ai_defense_score(self.persentase_dituduh)
        return describe_ai_defense_intent(score)

    def skor_defense(self) -> float:
        """Skor mentah 0-100, kalau butuh nilai gradasi (bukan cuma label)."""
        return calculate_ai_defense_score(self.persentase_dituduh)