"""
Value Network (Opsi C) untuk Shadow Heist -- KERANGKA, belum diuji terhadap engine asli.

File ini bukan skrip mandiri: potongannya ditempel ke sel-sel notebook yang sudah punya
baris_pemain, calon_aksi, urutkan_kandidat, putuskan, Ingatan, NAMA_SIMULASI, dst.

  Bagian 0  edit kecil di putuskan()                      -> notebook metode
  Bagian 1  fitur                                          -> notebook metode
  Bagian 2  pengumpul data (main_satu_game_data)           -> notebook metode (fuzzy / utility / BT)
  Bagian 3  training + evaluasi offline                    -> notebook baru (data dari 3 notebook digabung)
  Bagian 4  agen value network + pemasangan                -> notebook metode / notebook evaluasi

Keputusan desain (tulis di bab metodologi):
  * Yang dipelajari model hanya PEMILIHAN TARGET (vote, Hostage, Gag, Guard, Peek).
  * Waktu vote memakai aturan netral yang sama (tunggu sampai VOTE_TUNGGU_FRAKSI).
  * Chat tetap memakai keputusan_chat yang ada (agen hibrida).
  * Fitur HANYA kolom mentah. Jangan masukkan output sistem Mamdani (kecurigaan, ancaman, kambing_hitam, ...).
"""
import random

import numpy as np
import pandas as pd


# =====================================================================================
# Bagian 0 -- tambahkan dua kunci ini ke dictionary yang dikembalikan putuskan():
#
#     "kandidat_aksi": calon_aksi(ctx)[1],
#     "kandidat_vote": kandidat_vote(ctx),
#
# (dipakai untuk eksplorasi saat mengumpulkan data)
# =====================================================================================


# =====================================================================================
# Bagian 1 -- Fitur
# =====================================================================================
# Kolom mentah dari tabel hitung_bukti (= KOLOM_BUKTI tanpa "pemain").

FITUR_TARGET = ["tekanan", "dukungan", "inkonsistensi", "pengalihan", "serang_bersih", "dituduh_korban",
                "dorong_salah_eksekusi", "klaim", "p_sandera", "p_gag", "volume_info", "diam"]

# TODO: cek dulu dengan print(fitur.columns.tolist()) SEBELUM nilai_ancaman() / di fitur_lindung().
# Daftar di bawah masih tebakan dari alasan_ancaman() dan alasan_lindung(). Buang kolom yang
# ternyata dihitung dari output fuzzy (curiga: ancaman_sekarang, kecurigaan_publik, kepercayaan).
EKSTRA_HITMAN = ["menuduh_saya", "pengaruh", "klaim_peran", "tidak_dijaga", "ancaman_sekarang", "bicara_ronde_ini"]
EKSTRA_SPY = ["klaim_stalker", "pengaruh"]

JENIS = ["vote", "hostage", "gag", "guard", "peek"]


def _ekstra(df, kolom, target):
    """Fitur tambahan khusus role untuk satu target; KeyError bila nama kolom salah (sengaja, biar ketahuan)."""
    if df is None or target is None:
        return [0.0] * len(kolom)
    baris = df[df["pemain"] == target]
    if baris.empty:
        return [0.0] * len(kolom)
    b = baris.iloc[0]
    return [float(b[c]) for c in kolom]


def vektor(s, jenis, target):
    """
    Satu baris fitur untuk pasangan (situasi, aksi, target).
    s = dict dengan kunci: tabel, konteks, fitur_hitman, lindung, view.
        Saat inferensi s = ctx dari putuskan(); saat logging s dibuat dari hasil putuskan().
    """
    view, k = s["view"], s["konteks"]
    peran = view["saya"]["role"]
    n = max(1, len(view["pemain"]))
    if target is None:
        t, suara, gema = [0.0] * len(FITUR_TARGET), 0.0, 0.0
    else:
        b = baris_pemain(s["tabel"], target)
        t = [float(b[c]) for c in FITUR_TARGET]
        suara = float(k["porsi_suara"].get(target, 0.0))
        gema = min(1.0, k["gema_tuduh"].get(target, 0) / 3)
    if peran == "hitman":
        ekstra = _ekstra(s.get("fitur_hitman"), EKSTRA_HITMAN, target)
    elif peran == "spy":
        ekstra = _ekstra(s.get("lindung"), EKSTRA_SPY, target)
    else:
        ekstra = []
    konteks = [k["urgensi"], k["porsi_fase"], k["warga_bebas"] / n, k["hitman_hidup"] / n,
               k["ketidakjelasan"], k["sedikit_info"], view["ronde"] / 10, n / 10]
    return np.array(t + ekstra + [suara, gema] + konteks + [float(jenis == j) for j in JENIS], dtype=float)


def kandidat_vote(ctx):
    """Nama pemain yang layak di-vote; aturan sama dengan keputusan_vote / keputusan_vote_hitman."""
    if ctx["peran"] == "hitman":
        f = ctx["fitur_hitman"]
        return sorted(f[f["p_sandera"] < BATAS_SANDERA_VOTE]["pemain"])
    kandidat, _ = urutkan_kandidat(ctx["tabel"])
    layak = kandidat[(kandidat["p_sandera"] < BATAS_SANDERA_VOTE)
                     & ~kandidat["pemain"].isin(ctx["pengetahuan"]["bersih"])]
    return sorted(layak["pemain"])


# =====================================================================================
# Bagian 2 -- Pengumpul data
# =====================================================================================
def tim_menang(peran, pemenang):
    """1 bila tim si bot menang. ASUMSI: satu-satunya pemenang selain 'civilians' adalah tim Hitman."""
    if pemenang is None:
        return None
    return int((pemenang == "civilians") == (peran != "hitman"))


class Pencatat:
    """Menyimpan SATU baris per keputusan yang benar-benar dieksekusi (bukan tiap langkah simulasi)."""

    def __init__(self, metode):
        self.metode, self.baris = metode, {}

    def simpan(self, game_id, bot, peran, s, jenis, target, ronde):
        # kunci ini membuat eksekusi ganda di ronde yang sama menimpa, bukan menggandakan
        self.baris[(game_id, bot, ronde, jenis)] = {
            "game_id": game_id, "metode": self.metode, "peran": peran, "bot": bot, "ronde": ronde,
            "jenis": jenis, "target": target, "x": vektor(s, jenis, target)}

    def ke_dataframe(self, pemenang_per_game):
        df = pd.DataFrame(list(self.baris.values()))
        if df.empty:
            return df
        df["y"] = [tim_menang(p, pemenang_per_game[g]) for p, g in zip(df["peran"], df["game_id"])]
        df = df.dropna(subset=["y"]).copy()          # game tanpa pemenang (kena batas ronde) dibuang
        df["y"] = df["y"].astype(int)
        return df.reset_index(drop=True)


def jelajah(npc, hasil, rng, eps):
    """Dengan peluang eps, ganti TARGET (bukan jenis aksi) dengan kandidat sah acak."""
    if rng.random() >= eps:
        return npc
    if npc["action"] == "vote" and hasil["kandidat_vote"]:
        return {**npc, "target": rng.choice(hasil["kandidat_vote"])}
    if npc["action"] in AKSI_RAHASIA:
        pilihan = [c["target"] for c in hasil["kandidat_aksi"] if c["aksi"] == npc["action"]]
        if pilihan:
            return {**npc, "target": rng.choice(pilihan)}
    return npc


# Salinan main_satu_game; baris yang berubah ditandai "# <<<".
def main_satu_game_data(engine, rng, pintar, jumlah, pencatat, game_id, eps=0.0, rng_eks=None):  # <<<
    nama = NAMA_SIMULASI[:jumlah]
    match = engine.Match([], nama, rng=random.Random(rng.random()), now=0.0)
    match.npc_decisions = set()
    otak = {p.name: Ingatan(p.name) for p in match.players.values() if pintar(p.role)}
    label, catatan, t = {}, {"ilegal": 0, "vote_warga": 0, "vote_tepat": 0}, 0.0
    while match.phase != "finished" and match.round <= RONDE_MAKS_SIMULASI:
        ronde, fase = match.round, match.phase
        durasi = match.durations[fase]
        for langkah in range(1, LANGKAH_PER_FASE + 1):
            waktu = t + durasi * langkah / (LANGKAH_PER_FASE + 1)
            for nama_bot in sorted(otak):
                if not match.players[nama_bot].alive or match.phase == "finished":
                    continue
                ingatan = otak[nama_bot]
                view = ingatan.sinkron_snapshot(match.snapshot(nama_bot), waktu)
                for c in ingatan.chat:
                    if "intent" not in c:
                        intent, target = label.get(c["id"], ("neutral", []))
                        c.update(intent=intent, conf_intent=0.95, target=target)
                hasil = putuskan(ingatan, view)
                npc, rc = hasil["npc_decision"], hasil["rencana_chat"]
                # <<< baru: fitur, penanda "fakta pasti", eksplorasi
                s = {"tabel": hasil["tabel"], "konteks": hasil["konteks"], "fitur_hitman": hasil["fitur_hitman"],
                     "lindung": hasil["lindung"], "view": view}
                peran_bot = view["saya"]["role"]
                pasti = "sumber" in hasil["jejak_vote"].columns   # vote_pasti: aturan, bukan keputusan model
                if eps and rng_eks is not None and not (npc["action"] == "vote" and pasti):
                    npc = jelajah(npc, hasil, rng_eks, eps)
                # <<< akhir baru
                try:
                    if rc["kirim"]:
                        if not match.can_chat(nama_bot):
                            raise ValueError("chat tanpa izin")
                        rekaman = match.add_message(nama_bot, npc["message"])
                        label[rekaman["id"]] = _label_rencana(rc)
                        ingatan.catat_aksi_bot(view, rc)
                    if npc["action"] == "vote":
                        match.vote(nama_bot, npc["target"])
                        if match.players[nama_bot].role != "hitman":
                            catatan["vote_warga"] += 1
                            catatan["vote_tepat"] += match.players[npc["target"]].role == "hitman"
                        if not pasti:                                                         # <<<
                            pencatat.simpan(game_id, nama_bot, peran_bot, s, "vote", npc["target"], ronde)  # <<<
                    elif npc["action"] in AKSI_RAHASIA:
                        match.act(nama_bot, npc["action"], npc["target"])
                        ingatan.catat_aksi_rahasia(ronde, npc["action"], npc["target"])
                        pencatat.simpan(game_id, nama_bot, peran_bot, s, npc["action"], npc["target"], ronde)  # <<<
                except ValueError:
                    catatan["ilegal"] += 1
        for nama_bot in otak:
            match.npc_decisions.add((ronde, fase, nama_bot))
        t += durasi
        match.tick(t)
    return match.winner, match.round, catatan


def kumpulkan_data(engine, n_game, pintar, metode, eps=0.2, seed=7):
    """Jalankan n_game; kembalikan DataFrame (x = vektor fitur, y = tim bot itu menang)."""
    pencatat = Pencatat(metode)
    rng, rng_eks = random.Random(seed), random.Random(seed + 1)   # rng terpisah agar eksplorasi tidak menggeser engine
    pemenang = {}
    for g in range(n_game):
        gid = f"{metode}-{seed}-{g}"
        pemenang[gid], _, _ = main_satu_game_data(engine, rng, pintar, rng.randint(4, 10), pencatat, gid, eps, rng_eks)
    return pencatat.ke_dataframe(pemenang)


# Contoh pemakaian (di notebook metode):
#   engine = muat_engine()
#   df = kumpulkan_data(engine, 3000, lambda role: True, metode="fuzzy", eps=0.2)
#   df.to_pickle("data_fuzzy.pkl")
# Ulangi di notebook utility_ai dan behavior_tree, lalu gabungkan dengan pd.concat.


# =====================================================================================
# Bagian 3 -- Training + evaluasi offline (notebook baru)
# =====================================================================================
def latih(df, buat_model, frak_uji=0.2, seed=0):
    """Satu model per role. Pemisahan latih/uji PER GAME agar tidak bocor antar baris satu game."""
    from sklearn.metrics import log_loss, roc_auc_score
    games = np.array(sorted(df["game_id"].unique()))
    np.random.default_rng(seed).shuffle(games)
    uji = set(games[:int(len(games) * frak_uji)])
    model, laporan = {}, []
    for peran, d in df.groupby("peran"):
        dl, du = d[~d["game_id"].isin(uji)], d[d["game_id"].isin(uji)]
        m = buat_model().fit(np.vstack(dl["x"]), dl["y"].values)
        p = m.predict_proba(np.vstack(du["x"]))[:, 1]
        try:
            auc = roc_auc_score(du["y"], p)
        except ValueError:                      # data uji hanya satu kelas
            auc = float("nan")
        dasar = np.full(len(du), dl["y"].mean())  # pembanding: tebak rata-rata saja
        laporan.append({"peran": peran, "n_latih": len(dl), "n_uji": len(du), "AUC": round(auc, 3),
                        "logloss": round(log_loss(du["y"], np.clip(p, 1e-6, 1 - 1e-6), labels=[0, 1]), 3),
                        "logloss_dasar": round(log_loss(du["y"], np.clip(dasar, 1e-6, 1 - 1e-6), labels=[0, 1]), 3)})
        model[peran] = m
    return model, pd.DataFrame(laporan)


# from sklearn.ensemble import HistGradientBoostingClassifier
# from sklearn.linear_model import LogisticRegression
# model, laporan = latih(df, lambda: LogisticRegression(max_iter=2000))             # baseline
# model, laporan = latih(df, lambda: HistGradientBoostingClassifier(max_depth=4))   # pembanding


# =====================================================================================
# Bagian 4 -- Agen value network (pengganti penalaran; persepsi, kandidat, dan aturan engine tetap)
# =====================================================================================
def keputusan_aksi_vn(ctx, model):
    kemampuan, calon = calon_aksi(ctx)
    if not kemampuan or not ctx["view"]["saya"].get("can_act"):
        return rencana_aksi("tidak_bisa", alasan=["Tidak ada aksi rahasia yang tersedia saat ini."]), pd.DataFrame()
    if not calon:
        return rencana_aksi("tunggu", alasan=["Tidak ada target yang layak."]), pd.DataFrame()
    X = np.vstack([vektor(ctx, c["aksi"], c["target"]) for c in calon])
    p = model[ctx["view"]["saya"]["role"]].predict_proba(X)[:, 1]
    i = int(np.argmax(p))
    jejak = pd.DataFrame({"aksi": [c["aksi"] for c in calon], "target": [c["target"] for c in calon],
                          "prioritas": p})
    c = calon[i]
    return rencana_aksi(c["aksi"], c["target"], c["alasan"], float(p[i])), jejak


def keputusan_vote_vn(ctx, model):
    boleh, alasan = izin_vote(ctx["view"])
    if not boleh:
        return rencana_vote("tidak_bisa", alasan=[alasan]), pd.DataFrame()
    nama = kandidat_vote(ctx)
    if not nama:
        return rencana_vote("abstain", alasan=["Tidak ada kandidat yang layak di-vote."]), pd.DataFrame()
    if ctx["konteks"]["porsi_fase"] < VOTE_TUNGGU_FRAKSI:      # waktu vote: aturan netral yang sama untuk semua metode
        return rencana_vote("tunggu", alasan=["Menunggu diskusi dan suara lain."]), pd.DataFrame()
    X = np.vstack([vektor(ctx, "vote", n) for n in nama])
    p = model[ctx["view"]["saya"]["role"]].predict_proba(X)[:, 1]
    i = int(np.argmax(p))
    jejak = pd.DataFrame({"aksi": "vote", "target": nama, "prioritas": p})
    bot_alasan = None if ctx["peran"] == "hitman" else ctx["bot"]
    return rencana_vote("vote", nama[i], alasan_curiga(baris_pemain(ctx["tabel"], nama[i]), bot_alasan),
                        float(p[i])), jejak


def pasang_vn(model):
    """Ganti penalaran target di notebook ini. putuskan() mencari nama fungsi lewat global saat dipanggil."""
    global keputusan_aksi, keputusan_vote, keputusan_vote_hitman
    keputusan_aksi = lambda ctx: keputusan_aksi_vn(ctx, model)
    keputusan_vote = lambda ctx: keputusan_vote_vn(ctx, model)
    keputusan_vote_hitman = keputusan_vote
    # keputusan_chat, chat_pasti, vote_pasti, dan pertahanan_suara tidak diubah.

# Evaluasi: setelah pasang_vn(model), jalankan jalankan_simulasi(engine, n_game) yang sudah ada,
# lalu bandingkan menang_warga_% dan vote_tepat_% dengan konfigurasi fuzzy/utility/BT.
