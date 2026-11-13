# Prethesis: pelatihan AI bot Silent Terror

Repo ini berisi **notebook pelatihan dan laporan** untuk otak bot di game Silent Terror. Kode game, tempat bot benar-benar berjalan, ada di repo terpisah, **Games**.

Otak bot terdiri dari tiga bagian. Masing-masing punya notebook sendiri di folder `ai_2_dataset_baru/`:

| Bagian | Tugas | Notebook | Kode di game |
| --- | --- | --- | --- |
| **NLU** (IndoBERT) | Membaca chat pemain: niatnya apa (menuduh, membela, netral) dan siapa yang dituju | `nlu_baru.ipynb` (Model 1, intent), `nlu_target.ipynb` (Model 2, target) | `backend/app/bot/nlu.py` |
| **Fuzzy Mamdani** | Menimbang bukti, lalu memutuskan bicara apa, vote siapa, dan skill malam ke siapa | `npc_fuzzy.ipynb` | `backend/app/bot/fuzzy_controller.py`, folder `backend/app/bot/fuzzy/`, `backend/app/bot/ingatan.py` |
| **NLG** | Mengubah keputusan menjadi kalimat chat, lewat templat atau LLM (OpenRouter) | `npc_nlg.ipynb` | `backend/app/bot/nlg_controller.py` (main controller: urutan tahap), folder `backend/app/bot/nlg/` (satu file per tahap: `prompt.py`, `penulis.py`, `aturan.py`, `templat.py`, `pengaturan.py`) |

## Hubungan notebook dengan game

- **NLU:** notebook menghasilkan model. Model itu disalin ke game, lalu dipakai apa adanya.
- **Fuzzy dan NLG:** game memakai kode Python di `backend/app/bot/`. Notebook adalah **laporannya**. Bentuk kodenya tidak harus sama persis dengan game, tetapi logika, hitungan, urutan, nama fungsi, dan nama variabelnya sama. Jadi nama yang kamu temukan di notebook, misalnya `putuskan`, `hitung_bukti`, `pengetahuan_peran`, atau `kalimat_templat`, bisa langsung dicari di kode game.
- **Bukti kesamaan:** `npc_fuzzy.ipynb` menguji 328 skenario keputusan, lalu menjalankan simulasi pertandingan memakai engine game asli. Di repo Games, tes `backend/tests/test_skenario_fuzzy.py` dan `backend/tests/jejak/rekam_jejak.py --cek` memeriksa hal yang sama dari sisi game.

## Isi repo

```
prethesis/
├── README.md                  ← berkas ini
├── requirements.txt           paket Python (CUDA 12.1)
├── .env                       kunci API lokal, tidak ikut Git (lihat "Kunci LLM")
├── ai_2_dataset_baru/         ← FOLDER KERJA UTAMA
│   ├── nlu_baru.ipynb         Model 1: intent chat
│   ├── nlu_target.ipynb       Model 2: target dan relasi chat
│   ├── npc_fuzzy.ipynb        otak keputusan bot (Fuzzy Mamdani)
│   ├── npc_nlg.ipynb          penyusun kalimat bot (templat + LLM)
│   ├── data/                  dataset NLU dan bahan uji kalimat
│   ├── hasil_npc/             keluaran npc_fuzzy dan npc_nlg
│   ├── models/                model hasil training, tidak ikut Git (terlalu besar)
│   └── (notebook lain)        arsip, lihat bagian "Arsip"
├── ai_2_nlu_v1_janice/        arsip versi awal (NLU v1 dan fuzzy pertama)
├── lama/                      arsip dataset dan eksperimen NLU v1 sampai v3
└── reports/                   laporan audit, uji coba LLM, dan cadangan notebook
```

## Urutan menjalankan

Jalankan notebook dari dalam folder `ai_2_dataset_baru/`, dengan urutan berikut. Setiap notebook memakai hasil notebook sebelumnya.

| Urutan | Notebook | Masukan | Keluaran |
| --- | --- | --- | --- |
| 1 | `nlu_baru.ipynb` | `data/dataset_final3.csv`, `data/dataset_intent_tambahan.csv`, pesan dari sesi train dataset target | `models/notebook_standalone/intent_classifier_transformer/` |
| 2 | `nlu_target.ipynb` | `data/dataset_final3_context_target_pilot25_lengkap.csv`, `data/dataset_target_tambahan.csv` | `models/target_classifier/target_classifier_transformer/` (termasuk `ambang_target.json` dan `pair_builder.json`) |
| 3 | `npc_fuzzy.ipynb` | kedua model di atas, engine game `Games/backend/app/game/match_engine.py` | `hasil_npc/skenario_fuzzy.csv`, `hasil_npc/simulasi_fuzzy.csv`, `hasil_npc/nlg_fuzzy.jsonl` (rencana chat untuk NLG) |
| 4 | `npc_nlg.ipynb` | `hasil_npc/nlg_fuzzy.jsonl`, kedua model, dan LLM bila ada kuncinya | `hasil_npc/nlg_evaluasi_templat.csv`, `hasil_npc/nlg_evaluasi_llm.csv`, `hasil_npc/nlu_ketahanan_nama.csv` |

Notebook 1 dan 2 melatih IndoBERT, jadi sebaiknya dijalankan di komputer yang punya GPU NVIDIA. Di CPU tetap bisa, tetapi jauh lebih lama. Notebook 3 dan 4 hanya memakai model yang sudah jadi, sehingga cukup dijalankan di CPU.

### Letak folder

`npc_fuzzy.ipynb` membuka engine game lewat path relatif `../../../Games/backend/`. Karena itu, kedua repo harus diletakkan **bersebelahan** seperti ini:

```
a_skripsi/
├── Games/                     repo game
└── training/
    └── prethesis/             repo ini
```

## Menyiapkan lingkungan

1. Pasang Python **3.11**. Semua notebook disimpan dengan kernel `venv (3.11.9)`.
2. Buat dan aktifkan venv di root repo ini:
   ```
   python -m venv venv
   venv\Scripts\activate          (Windows)
   source venv/bin/activate       (Linux/macOS)
   ```
3. Pasang paket yang dipakai keempat notebook utama:
   ```
   pip install --extra-index-url https://download.pytorch.org/whl/cu121 "torch>=2.6.0" "transformers==4.46.3" datasets accelerate scikit-learn scikit-fuzzy optuna pandas numpy matplotlib tqdm joblib httpx jupyter
   ```
   `requirements.txt` juga berisi paket untuk notebook arsip, seperti LangChain dan klien LLM lama. Paket-paket itu tidak dibutuhkan untuk keempat notebook utama.
4. Pilih kernel `venv` di Jupyter atau VS Code, lalu jalankan notebook dari atas ke bawah.

### Kunci LLM (hanya untuk `npc_nlg.ipynb`)

`npc_nlg.ipynb` membaca berkas `.env` di root repo ini. Kalau berkas itu tidak ada, notebook membaca environment variable. Nilai kunci tidak pernah dicetak, dan berkas `.env` tidak ikut Git.

| Nama | Wajib? | Guna |
| --- | --- | --- |
| `OPENROUTER_API_KEY` | Tidak | Jalur LLM utama lewat OpenRouter. Nama `OPENROUTER_DEFAULT` dari game juga diterima. |
| `LLM_TAUTAN_URL` | Tidak | Jalur cadangan: LLM sendiri, misalnya Ollama di Docker yang dibuka lewat tunnel HTTPS (`Games/ai-docker`). |
| `LLM_TAUTAN_TOKEN`, `LLM_TAUTAN_MODEL` | Tidak | Token dan nama model untuk jalur tautan. |

Kalau tidak ada kunci sama sekali, notebook tetap berjalan sampai selesai: kalimat ditulis dengan templat, dan bagian evaluasi LLM dilewati.

Model OpenRouter bawaan notebook adalah `qwen/qwen3-14b`, sama dengan bawaan di `backend/app/bot/nlg/penulis.py` (`MODEL_OPENROUTER`). Server game bisa memakai model lain lewat `NPC_OPENROUTER_MODEL` atau pilihan di panel. Server produksi sekarang memakai `google/gemini-2.5-flash`.

## Memindahkan model ke game

Sesudah notebook 1 dan 2 selesai, salin isi kedua folder model ke repo Games:

| Dari (repo ini) | Ke (repo Games) |
| --- | --- |
| `ai_2_dataset_baru/models/notebook_standalone/intent_classifier_transformer/` | `backend/artifacts/indobert/intent/` |
| `ai_2_dataset_baru/models/target_classifier/target_classifier_transformer/` | `backend/artifacts/indobert/target/` |

Saat server dinyalakan, bot mencari model di tiga tempat dan memakai yang pertama ada (`folder_model` di `nlu.py`):

1. path dari pengaturan `NPC_INTENT_MODEL_DIR` dan `NPC_TARGET_MODEL_DIR`;
2. `backend/artifacts/indobert/intent/` dan `backend/artifacts/indobert/target/`;
3. folder `models/` di repo ini. Ini berlaku kalau kedua repo diletakkan bersebelahan seperti di atas, jadi di komputer sendiri model baru bisa langsung dicoba tanpa disalin.

Log `Otak NPC siap: NLU=indobert` menandakan model berhasil dimuat. Karena ukurannya besar, model tidak disimpan di Git kedua repo. Salinan model untuk server dikirim terpisah.

## Isi folder `data/`

| Berkas | Isi |
| --- | --- |
| `dataset_final3.csv` | 5.615 chat berlabel intent (`teks_chat`, `label_intent`). Data utama Model 1. |
| `dataset_intent_tambahan.csv` | 100 chat intent tambahan (27 Oktober 2026). Hanya dipakai di train IndoBERT. |
| `dataset_final3_context_target_pilot25_lengkap.csv` | 775 chat dalam sesi: pengirim, riwayat chat, daftar pemain, dan target. Data utama Model 2. |
| `dataset_target_tambahan.csv` | 500 sesi target tambahan (27 Oktober 2026). Hanya dipakai di train IndoBERT. |
| `ATURAN_LABEL.md` | Aturan memberi label intent dan target, dipakai saat relabel 26 Oktober 2026. |
| `relabel_2026-10-26.csv` | Catatan setiap baris yang labelnya diubah saat relabel: label lama dan label baru. |
| `manual_pilot_25/` | Bahan pembuatan dataset sesi target: prompt, sesi, hasil, dan log revisi. |
| `tambahan_2026-10-27/` | Bahan pembuatan dataset tambahan, beserta laporan dan alat pemeriksanya. |
| `uji_kalimat_rombak*.csv` | Kalimat uji bot (414 kasus) dan hasil bacaan IndoBERT pada Fase 5 dan Fase 8. |

Penjelasan lengkap cara dataset dibuat, setiap kasus, dan contohnya ada di dokumen **Dataset NLU** di panel game (menu 08).

## Dokumen penjelasan

Panel game (menu **08 Dokumen**) memuat dokumen HTML yang dibangun dari notebook dan dataset di repo ini. Kartunya bertanda **Training**. Teks, sel kode, dan keluarannya diambil dari notebook saat dokumen dibangun, jadi isinya sama dengan notebook pada saat itu. Bila notebook berubah, dokumennya perlu dibangun ulang:

| Dokumen | Sumber di repo ini | Pembangun (di folder `communicationfolder/` milik Games) |
| --- | --- | --- |
| Kode NLU Intent, Kode NLU Target, Diagram Alir NLU | `nlu_baru.ipynb`, `nlu_target.ipynb`, artefak di `models/` | `kode-ai-2026-10-26/sumber/` |
| Dataset NLU | folder `data/`, `nlu_baru.ipynb`, `nlu_target.ipynb` | `dataset-nlu-2026-11-13/sumber/` |
| Kode Fuzzy, Diagram Alir Fuzzy | `npc_fuzzy.ipynb` | `kode-ai-2026-10-26/sumber/` |
| Kode NLG | `npc_nlg.ipynb` | `kode-ai-2026-10-26/sumber/` |

Folder `communicationfolder/` hanya ada di komputer pengembang dan tidak ikut Git repo Games. Cara menjalankan tiap pembangun ada di README folder pembangunnya. Panel juga memuat dokumen bertanda **Backend** (dibangun dari kode game, misalnya Proses AI, Bedah Otak Fuzzy, dan Cara Kerja Bot) dan **Panduan** (Peta Dokumen), yang tidak bergantung pada notebook di sini.

## Arsip

Bagian-bagian di bawah ini disimpan sebagai riwayat. Isinya **tidak lagi mencerminkan game sekarang**, jadi jangan dipakai sebagai acuan.

| Letak | Isi |
| --- | --- |
| `ai_2_dataset_baru/npc_utility_ai.ipynb`, `npc_behavior_tree.ipynb` | Dua metode pembanding (Utility AI dan Behavior Tree). Sejak 3 November 2026 skripsi tidak lagi membandingkan metode, sehingga game hanya memakai Fuzzy. |
| `hasil_npc/*_utility*`, `hasil_npc/*_bt*`, `hasil_civilian/` | Keluaran lama kedua metode pembanding dan uji Civilian awal. |
| `ai_2_dataset_baru/nlu_lama.ipynb`, `nlu_gabungan.ipynb`, `nlu_intent_sesi.ipynb` | Eksperimen NLU lama: model v3, intent dan target dalam satu model, dan intent dari data sesi. |
| `ai_2_dataset_baru/ai_2_fuzzy.ipynb` | Laporan eksekusi fuzzy versi awal. |
| `ai_2_dataset_baru/panduan_kode_lokal/` | Panduan baca kode per 1 Oktober 2026, masih memakai tiga metode dan susunan backend lama. |
| `ai_2_nlu_v1_janice/`, `lama/` | NLU v1 sampai v3, dataset lama, dan generator dataset pertama. |
| `reports/` | Audit AI 1 Oktober 2026, uji coba LLM Bedrock dan Claude (September 2026), dan cadangan notebook sebelum dirombak. |

## Catatan

- Fase 10, yaitu melatih ulang IndoBERT, dikerjakan oleh pemilik repo. Sesudah run baru, catatan tanggal run (saat ini **27 Oktober 2026**) di markdown `nlu_baru.ipynb` dan `nlu_target.ipynb` perlu diperbarui.
- Branch kerja: `dev_andy`.
