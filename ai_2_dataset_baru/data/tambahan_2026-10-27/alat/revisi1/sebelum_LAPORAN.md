# Laporan dataset tambahan — 27 Oktober 2026

**Status: selesai, pemeriksaan otomatis LULUS.** 500 sesi target dan 100 chat intent disimpan terpisah dari dataset lama.

## Hasil dan lokasi

- [Dataset target tambahan](../dataset_target_tambahan.csv): 500 sesi, 14 kasus, 13 kolom, UTF-8 tanpa BOM, CRLF.
- [Dataset intent tambahan](../dataset_intent_tambahan.csv): 100 chat, 2 kolom, UTF-8 BOM, CRLF.
- [Pemeriksa](cek_tambahan.py), [hasil cek lengkap](alat/hasil_cek.json), [hasil impor](alat/laporan_impor.md).
- [Catatan revisi sesi](revisi_log.jsonl), [catatan revisi intent](alat/revisi_intent.json), [rekap tinjauan 500 sesi](alat/review_semantik.json).

## Jumlah target per kasus dan label

| Kasus | Defend | Offend | Neutral | Jumlah |
| --- | ---: | ---: | ---: | ---: |
| ambiguous | 25 | 25 | 0 | 50 |
| witness | 25 | 25 | 0 | 50 |
| mixed_relations | 0 | 50 | 0 | 50 |
| reference_start | 25 | 25 | 0 | 50 |
| short_history_1 | 25 | 13 | 12 | 50 |
| self | 25 | 25 | 0 | 50 |
| second_person | 13 | 12 | 0 | 25 |
| plural_reference | 13 | 12 | 0 | 25 |
| rhetorical_question | 13 | 12 | 0 | 25 |
| agreement | 13 | 12 | 0 | 25 |
| multiple_targets | 13 | 12 | 0 | 25 |
| interruption | 13 | 12 | 0 | 25 |
| first_message_unknown | 13 | 12 | 0 | 25 |
| neutral_status | 0 | 0 | 25 | 25 |
| **Total** | **216** | **247** | **37** | **500** |

Riwayat berisi 1.375 pesan; total pesan yang dianotasi pada sesi target adalah 1.875. Roster memakai 128 nama baru, tanpa nama yang sama dengan roster lama maupun NAMA_SEMU notebook.

## Komposisi intent

| Pola | Label | Jumlah |
| --- | --- | ---: |
| Peek membersihkan | defend | 50 |
| Klaim role + pembelaan | defend | 20 |
| Peek memberatkan | offend | 15 |
| Klaim role murni | neutral | 15 |

Total: 70 defend, 15 offend, 15 neutral. Pembagian pola disimpan terpisah di `alat/intent_manifest.json`; CSV tetap dua kolom.

## Alur, pengulangan, dan pemeriksaan makna

Pipeline manual lama disalin ke `alat/`; urutannya tetap prompts → jawaban JSON → import/validasi → export. Ada 500 job `_v02`, 50 prompt awal (10 job/prompt), dan 51 file jawaban termasuk satu perbaikan. Tidak ada job original atau panggilan API/model eksternal.

Schema, instruksi, dan validator salinan menerima target neutral sesuai ATURAN_LABEL.md. Validasi roster, bukti identitas, batas riwayat, intent utama, serta syarat kasus tetap dipertahankan. Sumber dipilih dari label terbaru dengan source_group unik yang belum dipakai pada target lama.

Impor pertama: **499 lolos, 1 gagal**. Job `r002088_v02` gagal karena bukti menunjuk pesan “role-ku” tanpa penanda aku. Prompt ulang dikerjakan dengan bukti pesan 1 yang menyebut nama pengirim secara eksplisit. Hasil akhir **500/500 lolos, 0 gagal**; `prompt_ulang/` kosong. Laporan awal dan prompt ulang awal diarsipkan di `alat/`.

Tinjauan makna menghasilkan **501 revisi pesan** di **59 sesi**: menyelaraskan selingan waktu pada second_person, memperjelas klaim pada riwayat rhetorical_question, dan menghapus rujukan reference_start yang bisa terbaca sebagai pembicara pertama. Sebanyak 40 riwayat reference_start juga ditulis ulang setelah sampel memperlihatkan pengulangan; hasil akhir mempunyai 50 utas panjang berbeda. Satu chat intent direvisi agar sumber hasil Peek eksplisit. Semua perubahan sesudah impor dicatat dengan sebelum/sesudah; kolom direvisi tetap False sesuai kontrak plan untuk keluaran baru.

Kalimat utama ditulis satu per satu oleh Codex, lalu nama diisikan dari roster. Reference_start memiliki 50 utas pendukung berbeda; beberapa pola riwayat pendek seperti permintaan penilaian atau pengumuman timer tetap dipakai ulang. Batas kemiripan yang diminta berlaku pada pesan utama. Ini data sintetis, dan tinjauan semantik oleh Codex belum merupakan pemeriksaan manusia independen. Sampel lengkap berikut disediakan untuk penilaian pemilik.

## Pemeriksaan otomatis

- Header dan urutan kolom sama persis dengan dataset lama; JSON kanonis, encoding dan CRLF benar.
- Fungsi `load_target_dataset` asli diekstrak melalui AST dan dijalankan sendiri pada CSV; tidak menjalankan cell training maupun mengubah notebook.
- Pengirim/target di roster, aturan neutral dan offend/defend diperiksa pada pesan utama serta semua 1.375 pesan riwayat.
- Session ID unik, 500 source_group unik, irisan source_group dengan data lama nol. Kalimat sumber yang identik dengan pesan utama lama juga disaring.
- Seluruh kuota tepat (tanpa memakai toleransi ±2), syarat kasus dan bukti acuan dari validator salinan lolos.
- 75 target tidak_diketahui; 25 pembelaan diri pada short_history_1; 12 bantahan klaim saksi yang hanya membela pengirim.
- 13 second_person menarget pembicara yang bukan pengirim terakhir; 7 interruption kembali membela diri sendiri.
- Seluruh 124.750 pasangan pesan utama diperiksa dengan batas atas aman dan SequenceMatcher dua arah: tidak ada kemiripan >0,9. Tidak ada pesan utama identik dengan pesan utama/riwayat target lama.
- Intent: label dan kuota empat pola benar, tidak ada duplikat setelah casefold dan normalisasi spasi, termasuk terhadap dataset intent lama.
- **23 uji pemeriksa lolos**, termasuk data rusak: ID/sumber bocor, JSON rusak, roster, aturan neutral, kuota, syarat kasus, kemiripan, dan duplikat intent. Cek pola intent memakai manifest hasil tinjauan ditambah penanda teks, bukan penilai semantik otomatis yang sempurna.

Jalankan ulang dari akar repo:

```powershell
venv\Scripts\python.exe ai_2_dataset_baru\data\tambahan_2026-10-27\cek_tambahan.py
venv\Scripts\python.exe ai_2_dataset_baru\data\tambahan_2026-10-27\alat\uji_pemeriksa.py
```

## Batas pekerjaan dan kondisi repo

Dataset lama dan kedua alat asli sama byte per byte dengan hash awal. Tidak ada training, perubahan notebook oleh alur ini, perubahan di Games, commit, atau push. Plan di Games hanya dibaca sebagai instruksi. Status Git awal sudah memuat perubahan dataset/notebook milik pengguna; detail dan hash disimpan di `alat/kondisi_awal.json`.

Windows tidak dapat menyimpan `laporan.md` dan `LAPORAN.md` sebagai dua file berbeda dalam folder yang sama. Karena itu hasil impor ditempatkan di `alat/laporan_impor.md`, sedangkan laporan akhir memakai nama `LAPORAN.md` ini.

**Perubahan bersamaan yang terdeteksi:** hash `nlu_gabungan.ipynb` berubah selama pekerjaan. Tidak ada operasi pekerjaan ini yang menulis file tersebut; penyebab eksternalnya belum dikonfirmasi. Notebook tidak ditimpa atau dipulihkan. Perubahan ini dicatat di hasil cek, terpisah dari syarat kelulusan dataset. Dataset lama, `nlu_target.ipynb`, `nlu_baru.ipynb`, dan alat asli masih cocok dengan hash awal.

Hash keluaran untuk pemeriksaan integritas:

| File | SHA-256 |
| --- | --- |
| dataset_target_tambahan.csv | `a7d2af672010c438ace6fbff62718c87dca88644ab409fbd7b57d334e153aee2` |
| dataset_intent_tambahan.csv | `1adade812a80eea5ce946447a2539e8b905b0d742ddf5faf101a2e0dce1d756b` |

## 20 sampel target untuk diperiksa

Pemilihan acak berstrata, seed **20261027**: satu sesi tiap kasus, ditambah satu lagi untuk enam kasus prioritas 1. Kasus prioritas 1 selain mixed_relations menampilkan satu defend dan satu label lainnya; stratum defend witness dipilih dari bantahan yang membela pengirim. Riwayat ditampilkan utuh agar acuan dan label konteks bisa diperiksa. Format relasi: pemain:relasi.

### 1. ambiguous — `r002913_v02`

Roster: Ghina, Savira, Salsabila, Tsania, Asih. Sumber CSV baris 2913.

| Posisi | Pengirim | Teks | Intent | Target |
| --- | --- | --- | --- | --- |
| Riwayat 1 | Asih | dua nama yang sedang dibahas itu Salsabila serta Ghina, catatannya belum dipisah. | neutral | Ghina:neutral, Salsabila:neutral |
| Riwayat 2 | Savira | catatan keduanya belum kupisah ke bagian masing-masing. | neutral | Ghina:neutral, Salsabila:neutral |
| **Utama** | **Tsania** | **gerak-geriknya bikin ragu, dia seperti sudah tahu siapa yang bakal disandera.** | **offend** | **tidak_diketahui:offend** |

### 2. rhetorical_question — `r001720_v02`

Roster: Rahma, Kirana, Nayla, Erlina, Ayuning. Sumber CSV baris 1720.

| Posisi | Pengirim | Teks | Intent | Target |
| --- | --- | --- | --- | --- |
| Riwayat 1 | Ayuning | aku sudah menuliskan klaim role dan penjelasan waktunya di chat. | neutral | [] |
| **Utama** | **Kirana** | **kamu mengira perubahan target mendadak itu wajar? Buatku jelas mencurigakan.** | **offend** | **Ayuning:offend** |

### 3. self — `r000787_v02`

Roster: Naura, Anindya, Feby, Aisyah, Zakia. Sumber CSV baris 787.

| Posisi | Pengirim | Teks | Intent | Target |
| --- | --- | --- | --- | --- |
| Riwayat 1 | Anindya | Naura mengaku Spy, sedangkan Aisyah belum menulis role. | neutral | Naura:neutral, Aisyah:neutral |
| Riwayat 2 | Zakia | semua yang belum menjelaskan boleh lanjut sekarang. | neutral | [] |
| **Utama** | **Feby** | **aku tadi cuma baca ulang chat, bukan sedang menyusun aksi Hitman. Jangan vote aku.** | **defend** | **Feby:defend** |

### 4. interruption — `r002058_v02`

Roster: Nadya, Haris, Izza, Amel, Khansa. Sumber CSV baris 2058.

| Posisi | Pengirim | Teks | Intent | Target |
| --- | --- | --- | --- | --- |
| Riwayat 1 | Haris | pembahasan kita masih tentang klaim Khansa dan alasan jeda chatnya. | neutral | Khansa:neutral |
| Riwayat 2 | Nadya | jam diskusi sudah berjalan, sisa tiga puluh detik. | neutral | [] |
| Riwayat 3 | Izza | belum berganti ronde, kolom diskusi tetap terbuka. | neutral | [] |
| **Utama** | **Amel** | **oke timer lanjut, aku akan vote Khansa. Cerita soal Guard-nya kedengaran ngarang.** | **offend** | **Khansa:offend** |

### 5. plural_reference — `r000285_v02`

Roster: Febi, Khansa, Cahya, Yasmin, Hafiz. Sumber CSV baris 285.

| Posisi | Pengirim | Teks | Intent | Target |
| --- | --- | --- | --- | --- |
| Riwayat 1 | Khansa | catat Yasmin dan Hafiz sebagai dua orang yang sama-sama belum membuka role. | neutral | Hafiz:neutral, Yasmin:neutral |
| Riwayat 2 | Cahya | aku sedang membaca catatan kedua orang itu sebelum memberi pendapat. | neutral | Hafiz:neutral, Yasmin:neutral |
| **Utama** | **Febi** | **Cahya, jangan termakan cerita mereka berdua; klaimnya terdengar palsu.** | **offend** | **Hafiz:offend, Yasmin:offend** |

### 6. ambiguous — `r000425_v02`

Roster: Nadira, Kirana, Amel, Zulfikar, Pandu. Sumber CSV baris 425.

| Posisi | Pengirim | Teks | Intent | Target |
| --- | --- | --- | --- | --- |
| Riwayat 1 | Amel | catatan soal jeda chat ini berlaku buat Kirana maupun Pandu. | neutral | Kirana:neutral, Pandu:neutral |
| Riwayat 2 | Nadira | dua klaim tersebut belum kita urutkan satu per satu. | neutral | Kirana:neutral, Pandu:neutral |
| **Utama** | **Zulfikar** | **aku tetap bela dia; mengulang pertanyaan bukan berarti sedang mengalihkan isu.** | **defend** | **tidak_diketahui:defend** |

### 7. short_history_1 — `r004605_v02`

Roster: Renata, Rahma, Nirmala, Luthfan, Asih. Sumber CSV baris 4605.

| Posisi | Pengirim | Teks | Intent | Target |
| --- | --- | --- | --- | --- |
| Riwayat 1 | Luthfan | aku mengaku Spy dan akan menulis catatan aksi setelah ini. | neutral | [] |
| **Utama** | **Asih** | **Luthfan yang baru klaim itu sus, alasannya terlalu dibuat-buat.** | **offend** | **Luthfan:offend** |

### 8. self — `r003006_v02`

Roster: Mahdi, Vanya, Ferdi, Tisna, Zahira. Sumber CSV baris 3006.

| Posisi | Pengirim | Teks | Intent | Target |
| --- | --- | --- | --- | --- |
| Riwayat 1 | Zahira | Ferdi mengaku Spy, sedangkan Tisna belum menulis role. | neutral | Ferdi:neutral, Tisna:neutral |
| Riwayat 2 | Vanya | semua yang belum menjelaskan boleh lanjut sekarang. | neutral | [] |
| **Utama** | **Mahdi** | **tetapkan saja aku sebagai pilihan vote terakhir, aku sudah pasrah.** | **offend** | **Mahdi:offend** |

### 9. mixed_relations — `r001945_v02`

Roster: Embun, Erlina, Isna, Marsha, Pandu. Sumber CSV baris 1945.

| Posisi | Pengirim | Teks | Intent | Target |
| --- | --- | --- | --- | --- |
| Riwayat 1 | Erlina | aku menaruh keterangan Isna pada bagian awal ringkasan. | neutral | Isna:neutral |
| Riwayat 2 | Embun | teks yang masuk belum berubah sejak disalin. | neutral | [] |
| **Utama** | **Marsha** | **dia layak dapat pembelaan setelah urutannya jelas; Pandu yang menurutku sengaja merusak urutan itu.** | **offend** | **Isna:defend, Pandu:offend** |

### 10. witness — `r003243_v02`

Roster: Nayla, Utari, Syauqi, Naufala, Rayhan. Sumber CSV baris 3243.

| Posisi | Pengirim | Teks | Intent | Target |
| --- | --- | --- | --- | --- |
| Riwayat 1 | Utari | hasil Peek yang aku laporkan menyebut Nayla Hitman, aku curiga Nayla. | offend | Nayla:offend |
| Riwayat 2 | Syauqi | semua boleh menanggapi catatan yang sudah dibagikan. | neutral | [] |
| **Utama** | **Nayla** | **tuduhan Utari nggak membuktikan aku jahat; aku memang Spy dan tidak melakukan Hostage.** | **defend** | **Nayla:defend** |

### 11. first_message_unknown — `r002032_v02`

Roster: Safira, Syauqi, Diandra, Wardana, Febi. Sumber CSV baris 2032.

| Posisi | Pengirim | Teks | Intent | Target |
| --- | --- | --- | --- | --- |
| **Utama** | **Safira** | **dia punya gelagat mencurigakan, aku memasukkannya ke daftar calon Hitman.** | **offend** | **tidak_diketahui:offend** |

### 12. neutral_status — `r000863_v02`

Roster: Izza, Salsabila, Damar, Syauqi, Arum. Sumber CSV baris 863.

| Posisi | Pengirim | Teks | Intent | Target |
| --- | --- | --- | --- | --- |
| Riwayat 1 | Syauqi | Izza, bisa jawab apa role atau aksi yang kamu laporkan malam ini? | neutral | Izza:neutral |
| **Utama** | **Izza** | **jawabanku singkat: aku Stalker dan sudah menggunakan Peek sekali.** | **neutral** | **Syauqi:neutral** |

### 13. multiple_targets — `r003245_v02`

Roster: Thalia, Ghani, Kinanti, Tania, Bagaskara. Sumber CSV baris 3245.

| Posisi | Pengirim | Teks | Intent | Target |
| --- | --- | --- | --- | --- |
| Riwayat 1 | Tania | catatan yang sedang kita bahas milik Kinanti dan Bagaskara, masing-masing sudah menulis klaim. | neutral | Kinanti:neutral, Bagaskara:neutral |
| **Utama** | **Ghani** | **jangan seret Kinanti maupun Bagaskara jadi pelaku hanya karena chatnya belum lengkap.** | **defend** | **Kinanti:defend, Bagaskara:defend** |

### 14. reference_start — `r001824_v02`

Roster: Jauhar, Bagaskara, Kinanti, Khalisa, Rasyid. Sumber CSV baris 1824.

| Posisi | Pengirim | Teks | Intent | Target |
| --- | --- | --- | --- | --- |
| Riwayat 1 | Bagaskara | pengakuan Stalker Kinanti belum menyertakan nama target Peek. | neutral | Kinanti:neutral |
| Riwayat 2 | Rasyid | buat semua, mari pisahkan pernyataan role dari rincian hasil skill. | neutral | [] |
| Riwayat 3 | Jauhar | aku mencatat role yang diakui pada bagian pertama. | neutral | [] |
| Riwayat 4 | Khalisa | bagian hasil masih berupa ruang untuk teks laporan berikutnya. | neutral | [] |
| Riwayat 5 | Bagaskara | klaim saja tidak menyebut siapa yang diperiksa. | neutral | [] |
| Riwayat 6 | Rasyid | apakah ada teks hasil di pesan lanjutan? Siapa pun yang membaca boleh menyalinnya. | neutral | [] |
| Riwayat 7 | Jauhar | di salinanku belum ada teks hasil pada urutan itu. | neutral | [] |
| Riwayat 8 | Khalisa | aku tandai kosong, bukan menambahkan nama dari dugaan. | neutral | [] |
| Riwayat 9 | Bagaskara | nama target skill dan pemain yang mengirim laporan harus berada di kolom berbeda. | neutral | [] |
| Riwayat 10 | Rasyid | iya, supaya nama pengirim tidak terbaca sebagai hasil Peek. | neutral | [] |
| Riwayat 11 | Jauhar | urutan pesan tetap kita pertahankan ketika menulis ringkasannya. | neutral | [] |
| Riwayat 12 | Khalisa | catatan role dan bagian yang belum dilaporkan sudah jelas terpisah. | neutral | [] |
| **Utama** | **Khalisa** | **aku kembali ke klaim di awal: dia ngarang, karena dua versinya nggak mungkin sama-sama benar.** | **offend** | **Kinanti:offend** |

### 15. witness — `r000996_v02`

Roster: Salma, Tania, Anindya, Larasati, Rasyid. Sumber CSV baris 996.

| Posisi | Pengirim | Teks | Intent | Target |
| --- | --- | --- | --- | --- |
| Riwayat 1 | Salma | catatanku tentang Tania sudah kubagikan ke grup sebelum sesi ini. | neutral | Tania:neutral |
| Riwayat 2 | Anindya | kita masih membahas ringkasan ronde ini. | neutral | [] |
| **Utama** | **Rasyid** | **aku setuju poin Salma: vote Tania, ceritanya soal Peek bertentangan dengan ucapannya sendiri.** | **offend** | **Tania:offend** |

### 16. mixed_relations — `r002801_v02`

Roster: Ajeng, Delima, Rosita, Sabrina, Nadhif. Sumber CSV baris 2801.

| Posisi | Pengirim | Teks | Intent | Target |
| --- | --- | --- | --- | --- |
| Riwayat 1 | Sabrina | catatan yang sedang terbuka adalah milik Delima. | neutral | Delima:neutral |
| Riwayat 2 | Ajeng | bagian klaim dan bagian hasilnya sudah terpisah di catatan. | neutral | [] |
| **Utama** | **Rosita** | **dia aman dari Peek yang kulakukan, tetapi Nadhif mesti diperiksa sebagai calon Hitman.** | **offend** | **Delima:defend, Nadhif:offend** |

### 17. second_person — `r001582_v02`

Roster: Salma, Arum, Zafran, Salsabila, Yasmin. Sumber CSV baris 1582.

| Posisi | Pengirim | Teks | Intent | Target |
| --- | --- | --- | --- | --- |
| Riwayat 1 | Zafran | aku minta kamu menanggapi klaimku, Salsabila, setelah membacanya. | neutral | Salsabila:neutral |
| Riwayat 2 | Salma | jam diskusi sudah berjalan, sisa tiga puluh detik. | neutral | [] |
| Riwayat 3 | Zafran | Salsabila, aku masih menunggu tanggapan soal klaim yang kuminta tadi. | neutral | Salsabila:neutral |
| **Utama** | **Salsabila** | **kamu yang menyapa aku tadi sepertinya ngarang. Aku tidak percaya klaim Stalker-mu.** | **offend** | **Zafran:offend** |

### 18. short_history_1 — `r003610_v02`

Roster: Almira, Kemal, Renata, Marsha, Isna. Sumber CSV baris 3610.

| Posisi | Pengirim | Teks | Intent | Target |
| --- | --- | --- | --- | --- |
| Riwayat 1 | Almira | yang kucurigai Isna; tidak menjawab pertanyaan aksi itu aneh. | offend | Isna:offend |
| **Utama** | **Isna** | **yang ditulis tadi cuma potongan ucapanku. Aku nggak bersalah.** | **defend** | **Isna:defend** |

### 19. reference_start — `r000394_v02`

Roster: Astri, Hanif, Thalia, Yudhis, Anindya. Sumber CSV baris 394.

| Posisi | Pengirim | Teks | Intent | Target |
| --- | --- | --- | --- | --- |
| Riwayat 1 | Yudhis | di laporan Hanif, urutan diskusi dan malam tertulis terbalik. | neutral | Hanif:neutral |
| Riwayat 2 | Anindya | aku sedang membaca apakah urutan tulisan memang dimaksudkan sebagai urutan kejadian. | neutral | [] |
| Riwayat 3 | Astri | buat semua, kalimat pertama dimulai dengan ringkasan ronde. | neutral | [] |
| Riwayat 4 | Thalia | kalimat kedua baru menyebut kejadian malam. | neutral | [] |
| Riwayat 5 | Yudhis | ringkasan bisa saja ditempatkan sebelum rincian dalam sebuah pesan. | neutral | [] |
| Riwayat 6 | Anindya | jadi posisi kalimat tidak otomatis sama dengan waktu kejadian. | neutral | [] |
| Riwayat 7 | Astri | aku tandai pengantar ringkasan secara terpisah. | neutral | [] |
| Riwayat 8 | Thalia | kata sebelum dan sesudah tetap disalin persis. | neutral | [] |
| Riwayat 9 | Yudhis | iya, dua kata itu penting untuk membaca urutan waktu. | neutral | [] |
| Riwayat 10 | Anindya | nomor malam juga tidak akan kutukar sendiri. | neutral | [] |
| Riwayat 11 | Astri | catatan lengkap akan mempertahankan susunan kalimat asli. | neutral | [] |
| Riwayat 12 | Thalia | oke, kita bisa membahas urutannya dengan teks yang sudah jelas. | neutral | [] |
| **Utama** | **Thalia** | **pembahasan panjang ini tidak membuat dia layak divote. Aku masih percaya dia warga.** | **defend** | **Hanif:defend** |

### 20. agreement — `r001995_v02`

Roster: Mahesa, Asih, Dyah, Ayuning, Habib. Sumber CSV baris 1995.

| Posisi | Pengirim | Teks | Intent | Target |
| --- | --- | --- | --- | --- |
| Riwayat 1 | Ayuning | vote Mahesa jadi saranku karena alasan pindah pilihannya janggal. | offend | Mahesa:offend |
| Riwayat 2 | Habib | sebentar, sisa waktunya satu menit di layarku. | neutral | [] |
| **Utama** | **Asih** | **iya, aku setuju penilaian itu. Masukkan yang dibahas tadi ke daftar vote.** | **offend** | **Mahesa:offend** |

## 20 sampel intent untuk diperiksa

Acak berstrata dengan seed yang sama: 10 Peek membersihkan, 4 klaim+pembelaan, 3 Peek memberatkan, 3 klaim murni. Nomor baris mencakup header CSV.

| Baris CSV | Pola | Teks | Label |
| ---: | --- | --- | --- |
| 51 | peek_membersihkan | untuk Zafran hasil Peek yang kudapat membersihkan dia, bukan Hitman | defend |
| 93 | klaim_murni | aku menyatakan Civilian di pembahasan role sekarang | neutral |
| 7 | peek_membersihkan | Wening jangan diseret, di layar hasil Peek-ku tertulis bukan Hitman | defend |
| 81 | peek_memberatkan | Aisyah terbaca Hitman di hasil Peek-ku, aku mau menuduh dia | offend |
| 77 | peek_memberatkan | Syifa Hitman dari laporan skill-ku semalam, arahkan vote ke dia | offend |
| 21 | peek_membersihkan | Renata nggak jahat dari hasil Peek aku, jangan buru-buru eksekusi | defend |
| 83 | peek_memberatkan | Fathia terindikasi Hitman dari Peek semalam, bukan cuma feeling gw | offend |
| 42 | peek_membersihkan | Bagaskara ternyata bukan Hitman setelah kucek menggunakan Peek | defend |
| 14 | peek_membersihkan | aku stalker ya, dan hasilku ke Mahesa bilang dia bukan pelaku | defend |
| 43 | peek_membersihkan | gw melaporkan Wardana aman berdasarkan Peek, jangan salah vote | defend |
| 19 | peek_membersihkan | hasil peek semalam buat si L: Civilian, tolong catat pembelaan ini | defend |
| 38 | peek_membersihkan | peek ke Banyu selesai, hasilnya justru membela dia: bukan Hitman | defend |
| 50 | peek_membersihkan | gw intip Haikal semalam dan yang kebaca warga biasa, stop tuduh dia | defend |
| 36 | peek_membersihkan | si U terbaca bukan Hitman, itu laporan hasil Peek-ku ronde ini | defend |
| 96 | klaim_murni | gw warga biasa, cuma mau melengkapi daftar klaim | neutral |
| 62 | klaim_pembelaan | aku Spy, jadi tuduhan bahwa aku menyandera orang itu tidak benar | defend |
| 68 | klaim_pembelaan | aku Spy, jangan desak aku memberikan hasil pengintaian palsu | defend |
| 56 | klaim_pembelaan | aku bukan Hitman, aku warga biasa; itu sebabnya nggak ada skill buat kulaporkan | defend |
| 64 | klaim_pembelaan | role gw Stalker, tolong jangan eksekusi gw dari dugaan semata | defend |
| 88 | klaim_murni | role gw Civilian, itu info yang mau kutulis dulu | neutral |

## Pemakaian berikutnya

Integrasi ke bagian train dan penyisihan uji tambahan dilakukan pemilik proyek sesudah peninjauan. CSV tambahan belum digabung ke dataset lama, sehingga pekerjaan ini tidak mengubah pembagian test lama atau menghasilkan angka evaluasi model baru.
