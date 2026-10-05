# Audit NLU, target, fuzzy, utility AI, dan behavior tree

Tanggal: 1 Oktober 2026. Proyek: Games dan notebook ai_2_dataset_baru.

## Kesimpulan

Belum sepenuhnya benar. Logika dasar dan pengujian yang sudah tersedia sebagian besar lulus, tetapi audit tambahan menemukan kesalahan prediksi target serta celah integrasi yang dapat mengubah bukti dan keputusan bot. Audit ini tidak mengubah kode game, notebook, atau bobot model; hanya menambahkan laporan dan skrip reproduksi di folder ini.

## Temuan prioritas

### 1. P1 — Model target membalik relasi pada kalimat campuran

Reproduksi dengan IndoBERT asli, CPU, roster Nara/Andi/Budi/Citra/Dodi/Eka, pengirim Andi, tanpa riwayat:

> Budi mencurigakan, tapi Citra bukan Hitman.

Harapan: offend Budi, defend Citra. Aktual: **defend Budi (0,9632), offend Citra (0,9861)**. Intent offend memiliki confidence 0,99984, sehingga filter MIN_CONF_INTENT tidak membuang pesan ini. Ketiga metode mengambil relasi tersebut sebagai bahan bukti dan bisa menilai pemain yang salah.

Contoh lain: “Menurutku Budi bukan Hitman.” terklasifikasi offend dengan confidence 0,3944 dan target offend Budi. Contoh kedua memang dibuang oleh filter confidence intent 0,60 saat pembentukan bukti; contoh kalimat campuran pertama tidak.

Lokasi inferensi: [nlg.py](C:/Users/andyc/Documents/a_skripsi/Games/backend/services/npc_brain/generated/nlg.py:480), target pada baris 490; pemakaian bukti: [otak_fuzzy.py](C:/Users/andyc/Documents/a_skripsi/Games/backend/services/npc_brain/generated/otak_fuzzy.py:599), juga salinan utility dan BT.

Perbaikan: perluas evaluasi kalimat campuran/negasi dengan pertukaran urutan nama dan klausa; periksa contoh training yang relevan; gunakan validation untuk pemilihan perbaikan dan test terpisah untuk pelaporan. Ini kesalahan prediksi yang terbukti, bukan bukti bahwa seluruh model buruk atau seluruh label tertukar. Lima smoke input ini bukan estimasi akurasi populasi.

Bukti: [nlu_smoke.json](nlu_smoke.json), [nlu_smoke.py](nlu_smoke.py).

### 2. P1 — Urutan bukti bergantung pada UUID pesan

Semua pesan yang baru ditemukan dalam satu snapshot diberi waktu_terima yang sama. hitung_bukti lalu mengurutkannya menurut ronde, fase, waktu, **id**. ID dari engine adalah UUID acak; urutan leksikografis UUID tidak mewakili waktu kirim.

Reproduksi pada ketiga metode: Andi menuduh Budi, kemudian Budi menuduh Citra. Hanya mengganti urutan leksikografis ID mengubah nilai pengalihan Budi dari **0,5 menjadi 0,0**, tanpa mengubah teks atau urutan pesan aslinya. Pengaruh, pendorong eksekusi pertama, dan perubahan sikap juga bergantung pada kronologi.

Lokasi: [match_engine.py](C:/Users/andyc/Documents/a_skripsi/Games/backend/services/match_engine.py:440), [sinkron_snapshot](C:/Users/andyc/Documents/a_skripsi/Games/backend/services/npc_brain/generated/otak_fuzzy.py:457), [hitung_bukti](C:/Users/andyc/Documents/a_skripsi/Games/backend/services/npc_brain/generated/otak_fuzzy.py:695). Berlaku juga untuk utility dan BT.

Perbaikan: simpan waktu/nomor urut monoton pada pesan di engine, teruskan ke snapshot dan memori, gunakan nomor urut sebagai pemutus seri. Pertahankan urutan snapshot untuk kompatibilitas pesan lama; jangan mengurutkan UUID sebagai kronologi.

Bukti: uuid_changes_evidence pada [recheck.json](recheck.json).

### 3. P1 — Chat dan vote terakhir bisa salah ronde atau hilang dari memori

Snapshot chat tidak membawa ronde/fase/waktu kirim. Bot menebaknya dari fase saat polling. Vote yang disimpan saat transisi hanya vote yang sempat terlihat pada polling sebelumnya.

Reproduksi dengan Match asli: bot membaca Tribunal ronde 1 pada t=98; Andi mengirim tuduhan dan Andi/Nara vote Budi sebelum deadline t=100; bot membaca lagi pada t=101. Aktual:

- Budi tercatat dieksekusi pada ronde 1.
- Chat Andi tercatat **day ronde 2**, padahal dikirim saat Tribunal ronde 1.
- **Memori vote kosong**, termasuk vote milik Nara sendiri.

Dampak: bukti pendorong eksekusi dan dugaan Hostage/Gag tidak lengkap; peluruhan bukti serta status “sudah bicara ronde ini” salah. Ini terjadi saat event masuk di antara polling terakhir dan deadline, bukan pada setiap pesan.

Lokasi: [sinkron_snapshot](C:/Users/andyc/Documents/a_skripsi/Games/backend/services/npc_brain/generated/otak_fuzzy.py:415), baris 457–465; [penerapan vote](C:/Users/andyc/Documents/a_skripsi/Games/backend/services/npc_service.py:354). Berlaku pada ketiga metode.

Perbaikan: metadata chat dari engine; riwayat hasil Tribunal publik yang tetap tersedia setelah transisi; catat vote bot sendiri setelah berhasil diterapkan. Jangan mengandalkan polling terakhir untuk merekonstruksi hasil final.

Bukti: [phase_edge.json](phase_edge.json), [phase_edge.py](phase_edge.py).

### 4. P2 — Behavior tree melewati pembatas anti-gema

Daftar calon_chat sudah menolak tuduhan ketika dua pemain lain menuduh target yang sama. Namun _k_tersangka mengambil langsung urutan tersangka dan _a_tuduh membuat rencana baru, tanpa mengecek kandidat yang telah disaring.

Reproduksi memakai skenario dan fixture anti-gema yang sudah ada di notebook: gema_tuduh[Dodi] = 2. Fuzzy dan utility memilih ajak_bicara; BT tetap memilih **tuduh Dodi**. Tes notebook lama lulus karena memeriksa daftar kandidat dan urutan tersangka, bukan larangan pada keputusan chat akhir.

Lokasi: [otak_bt.py](C:/Users/andyc/Documents/a_skripsi/Games/backend/services/npc_brain/generated/otak_bt.py:1712), _a_tuduh pada baris 1723. Sumber: npc_behavior_tree.ipynb bagian Pohon Chat dan Pengujian.

Perbaikan: cabang tuduh BT harus memilih kandidat tuduh yang lolos pembatas bersama, termasuk anti-gema dan riwayat ungkap. Tambahkan assertion terhadap rencana_chat dari putuskan().

Bukti: echo_repro pada [recheck.json](recheck.json).

### 5. P2 — Validasi NLG menerima target tambahan di luar rencana

validasi_nlu hanya memastikan pasangan target yang diminta ada dalam prediksi; target_lain dicatat tetapi tidak menyebabkan penolakan. Pemeriksa aturan juga membolehkan nama yang muncul dalam bukti, walaupun nama itu bukan target tindakan.

Reproduksi dengan NLU tiruan untuk mengisolasi validator: rencana offend Budi, bukti menyebut Budi dan Citra, keluaran “Aku curiga Budi dan Citra.”. Prediksi offend Budi + offend Citra diterima dengan **lolos=true**, sementara target_lain berisi Citra. Ini bertentangan dengan kontrak “jangan menambah atau mengganti target”.

Lokasi: [nlg.py](C:/Users/andyc/Documents/a_skripsi/Games/backend/services/npc_brain/generated/nlg.py:333), [validasi_nlu](C:/Users/andyc/Documents/a_skripsi/Games/backend/services/npc_brain/generated/nlg.py:537).

Perbaikan: bedakan menyebut pemain sebagai sumber bukti dengan menjadikannya target relasi; tolak relasi tambahan yang tidak diizinkan rencana. Pertahankan pengecualian bela_diri secara eksplisit.

Bukti: nlg_extra_target_accepted pada [recheck.json](recheck.json). Reproduksi ini menguji validator, bukan mengklaim LLM selalu menghasilkan kalimat tersebut.

### 6. P2 — Username berupa kata ganti/istilah game mengubah makna NLU

samarkan_nama dan varian_nama_intent memeriksa exact username sebelum KATA_GANTI/ISTILAH_GAME. Username seperti aku dan hitman memenuhi pola username dan tidak tercantum dalam daftar nama sistem yang dicadangkan di kode.

Dengan roster Nara/aku/hitman, teks “aku bukan hitman” untuk kandidat hitman menjadi **PEMAIN_X bukan KANDIDAT_X**. Kalimat pembelaan diri berubah menjadi relasi antarpemain. Masalah berlaku pada input kedua model; ini bukti kegagalan preprocessing, bukan pengukuran prediksi model untuk semua username tersebut.

Lokasi: [nlg.py](C:/Users/andyc/Documents/a_skripsi/Games/backend/services/npc_brain/generated/nlg.py:378) dan baris 401; [schemas/auth.py](C:/Users/andyc/Documents/a_skripsi/Games/backend/schemas/auth.py:38). Fungsi serupa ada di notebook target dan ketiga notebook NPC.

Perbaikan: tetapkan kontrak nama ambigu—misalnya identitas tampilan yang tidak bertabrakan atau penanda mention eksplisit—dan uji kalimat kata ganti/role. Sekadar membalik urutan pengecekan membuat penyebutan username ambigu tidak dikenali; kebijakannya harus konsisten dari akun sampai NLU.

Bukti: name_collision pada [recheck.json](recheck.json).

### 7. P2 — Cadangan NLG tetap dapat mengirim teks yang gagal pemeriksaan aturan

Jika seluruh templat gagal aturan, tulis_pesan memakai seluruh daftar dinilai sebagai kandidat cadangan, lalu mengembalikan salah satunya. _kirim_chat hanya memeriksa teks, fase, dan hak bicara, tanpa memeriksa lolos_aturan.

Reproduksi: target username bot menghasilkan “Aku curiga sama bot.” dengan **lolos_aturan=false**, pelanggaran menyebut_ai, tetapi tetap dikembalikan sebagai teks final. Pada contoh ini pemicu merupakan benturan nama yang valid dengan regex, bukan kebocoran identitas NPC. Masalah umumnya adalah hasil penolakan aturan tidak menjadi syarat kirim.

Lokasi: [nlg.py](C:/Users/andyc/Documents/a_skripsi/Games/backend/services/npc_brain/generated/nlg.py:1061), [npc_service.py](C:/Users/andyc/Documents/a_skripsi/Games/backend/services/npc_service.py:382).

Perbaikan: bedakan kebijakan toleransi salah baca NLU dengan pelanggaran aturan; gunakan cadangan yang benar-benar lolos aturan atau batalkan chat. Sesuaikan deteksi istilah agar username valid tidak otomatis dianggap menyebut AI.

Bukti: nlg_unsafe_fallback pada [recheck.json](recheck.json).

## Yang sudah diverifikasi

- Sidik keempat modul ekspor (fuzzy, utility, BT, NLG) cocok dengan notebook sumber. Tidak ditemukan ekspor kedaluwarsa pada pemeriksaan ini.
- SHA-256 bobot model, config, dan tokenizer untuk intent serta target di Games cocok dengan file hasil training.
- **135/135 skenario**: 45 per metode lulus.
- Assertion notebook bersama dan khusus metode lulus: 21 kelompok fuzzy, 20 utility, 18 BT. Termasuk legalitas keputusan, batas informasi privat, determinisme, adaptor snapshot, serta grid/input fuzzy dan semantik node BT yang tersedia.
- **69/69 tes gabungan** test_npc_brain, test_npc_ketahanan, test_match_engine, test_match_simulations, test_victory_rules lulus.
- Suite test_npc*.py: **59/60 lulus** memakai Python global dan dependency lokal Games/tmp/profile-test-deps. Satu gagal karena paket anthropic tidak tersedia pada environment ini; jalur Claude tidak dapat dibuat. Ini kendala environment pengujian, bukan temuan bug skor atau pemilihan target.
- IndoBERT asli berhasil dimuat dan diuji dengan venv proyek. Dari lima smoke input manual, ditemukan dua keluaran salah di atas; tiga contoh tuduhan langsung, bela diri, dan neutral sesuai harapan. Tidak mengartikan sampel kecil ini sebagai akurasi 60%.
- Logika fuzzy memiliki cakupan aturan/input yang lolos tes tersedia. Utility IAUS/kurva dan semantik Selector/Sequence BT juga lolos tes tersedia. Temuan bersama di preprocessing/memori tetap memengaruhi hasil ketiganya walaupun rumus dan unit test lulus.

## Batas pemeriksaan

Audit mencakup sumber training/split dan pembentukan pasangan, model tersimpan, inferensi smoke asli, seluruh inti penalaran yang dipakai runtime, memori snapshot, kandidat aksi, penerapan keputusan, serta validasi target keluaran. Tidak melakukan training ulang, evaluasi ulang seluruh dataset test, pertandingan manusia langsung, pengujian beban banyak room, atau panggilan provider LLM/DB produksi. Angka metrics.json target merupakan metrik tersimpan dengan input/konteks evaluasi notebook, bukan hasil evaluasi ulang pipeline live oleh audit ini.

Python global tidak cocok untuk inferensi Transformers lokal; venv proyek dapat menjalankan model tetapi dependency backend-nya belum lengkap. Tes backend dijalankan dengan Python global + dependency lokal yang sudah tersedia. Log percobaan tersimpan agar hasil bisa dibedakan dari masalah environment. Stack trace otak rusak/ImportError x pada tes ketahanan adalah kegagalan yang sengaja disimulasikan oleh tes.

## Reproduksi

Jalankan dari Games/backend. Tidak membutuhkan jaringan atau database produksi.

- python -B C:/Users/andyc/Documents/a_skripsi/training/prethesis/reports/audit_ai_20261001/recheck.py
- python -B C:/Users/andyc/Documents/a_skripsi/training/prethesis/reports/audit_ai_20261001/phase_edge.py
- C:/Users/andyc/Documents/a_skripsi/training/prethesis/venv/Scripts/python.exe -B C:/Users/andyc/Documents/a_skripsi/training/prethesis/reports/audit_ai_20261001/nlu_smoke.py

Skrip audit memakai helper/skenario dari notebook tanpa menjalankan sel training, unduhan model, pemanggilan LLM, atau penulisan hasil eksperimen notebook. recheck.py merekam kegagalan assertion ke JSON; periksa isinya, jangan hanya exit code.

Urutan perbaikan yang disarankan: kronologi dan event final dari engine → pembatas BT dan validator → preprocessing nama → penguatan evaluasi/model target. Perubahan logika generated harus berasal dari notebook lalu diekspor kembali.
