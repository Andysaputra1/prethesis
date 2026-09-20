from __future__ import annotations

from dataclasses import dataclass, field

# Bobot bias: seberapa besar kecenderungan Hitman untuk ikut menuduh (accusing)
# dibanding intent lain saat memilih/generate chat.
HITMAN_ACCUSING_BIAS = 1.6  # pengali probabilitas relatif terhadap bobot dasar


@dataclass
class HitmanKnowledge:
    """Ground-truth yang diketahui seorang Hitman tentang timnya sendiri.

    Berbeda dari CivilianSuspicionTracker (yang menebak lewat fuzzy logic karena
    tidak tahu identitas asli lawan), seorang Hitman TIDAK perlu inferensi untuk
    hal ini -- dia tahu pasti siapa saja rekan Hitman lain kalau di sesi ini
    jumlah Hitman lebih dari satu.
    """

    player_id: str
    rekan_hitman: set[str] = field(default_factory=set)  # id pemain Hitman lain (kalau >1)

    def tambah_rekan(self, teman_id: str) -> None:
        """Daftarkan seorang pemain lain sebagai sesama Hitman (skip diri sendiri)."""
        if teman_id != self.player_id:
            self.rekan_hitman.add(teman_id)

    def is_rekan(self, pemain_id: str) -> bool:
        """True kalau pemain_id adalah sesama Hitman (bukan dirinya sendiri)."""
        return pemain_id in self.rekan_hitman

    def is_diri_sendiri(self, pemain_id: str) -> bool:
        return pemain_id == self.player_id

    def punya_rekan(self) -> bool:
        """True kalau sesi ini punya >1 Hitman (jadi si Hitman ini tidak sendirian)."""
        return len(self.rekan_hitman) > 0


def assign_hitman_team(hitman_ids: list[str]) -> dict[str, HitmanKnowledge]:
    """Bangun HitmanKnowledge untuk tiap Hitman di awal game.

    Dipanggil sekali saat role assignment, supaya SEMUA Hitman di sesi ini
    langsung saling tahu identitas satu sama lain -- ini yang menjawab kasus
    "kalau Hitman ada dua, masing-masing harus tahu siapa temannya". Hitman
    TIDAK diberi tahu siapa Spy atau Stalker -- identitas role civilian tetap
    tersembunyi dari Hitman, sama seperti dari pemain lain.

    Args:
        hitman_ids: daftar id semua pemain yang mendapat peran Hitman di sesi ini.

    Returns:
        Mapping id pemain -> HitmanKnowledge miliknya (sudah terisi rekan_hitman).
    """
    knowledge_map: dict[str, HitmanKnowledge] = {
        pid: HitmanKnowledge(player_id=pid) for pid in hitman_ids
    }
    for pid, knowledge in knowledge_map.items():
        for other_id in hitman_ids:
            knowledge.tambah_rekan(other_id)
    return knowledge_map


def pilih_bobot_intent_hitman(
    kandidat_intent: list[str],
    bobot_dasar: dict[str, float],
    bias_accusing: float = HITMAN_ACCUSING_BIAS,
) -> dict[str, float]:
    """Sesuaikan bobot probabilitas intent chat sesuai persona Hitman.

    Persona Hitman: senang ikut menuduh (accusing) untuk mengalihkan kecurigaan
    dari dirinya sendiri. Fungsi ini menaikkan bobot intent 'accusing' relatif
    terhadap intent lain, lalu me-renormalisasi supaya tetap jadi distribusi
    probabilitas yang valid (total = 1). Fungsi ini tidak menentukan SIAPA yang
    dituduh -- itu keputusan terpisah (mis. bisa dibuat cenderung menghindari
    menuduh rekan_hitman miliknya sendiri lewat HitmanKnowledge.is_rekan).

    Args:
        kandidat_intent: daftar intent yang tersedia untuk dipilih giliran ini.
        bobot_dasar: bobot probabilitas awal per intent, sebelum bias persona.
        bias_accusing: pengali bobot untuk intent 'accusing'.
    """
    bobot_tersesuaikan = dict(bobot_dasar)
    if "accusing" in kandidat_intent and "accusing" in bobot_tersesuaikan:
        bobot_tersesuaikan["accusing"] *= bias_accusing

    total = sum(bobot_tersesuaikan.get(intent, 0.0) for intent in kandidat_intent)
    if total <= 0:
        return {intent: 1.0 / len(kandidat_intent) for intent in kandidat_intent}
    return {intent: bobot_tersesuaikan.get(intent, 0.0) / total for intent in kandidat_intent}
