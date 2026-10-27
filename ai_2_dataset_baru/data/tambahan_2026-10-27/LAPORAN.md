# Laporan dataset tambahan — 27 Oktober 2026

**Status Revisi 1: selesai, pemeriksaan otomatis LULUS.** 500 sesi target dan 100 chat intent disimpan terpisah dari dataset lama. Seluruh 1.375 konteks sudah ditulis ulang; anotasi dan struktur sesi tetap identik.

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

Pada **Revisi 1**, 1375 teks konteks, 28 teks utama yang memuat tema pencatatan/pembelaan sebagai pengumuman, serta 11 chat intent diperbarui. Label, target, bukti, pengirim, roster, jumlah/urutan pesan, ID, sumber, dan metadata kasus dipertahankan. **500/500 sesi revisi diimpor ulang, tanpa kegagalan.** Opsi --revalidate memastikan checkpoint lama tidak otomatis dihitung sebagai revisi yang lolos. Log keseluruhan berisi 1904 perubahan pesan, termasuk 501 perubahan dari putaran awal; log khusus Revisi 1 tersimpan terpisah di alat/revisi1/revisi_log.jsonl.

Kalimat utama yang tidak memerlukan perubahan gaya tetap dipertahankan. Seluruh konteks hasil revisi unik setelah huruf kecil dan spasi dinormalisasi; tidak ada satu kalimat konteks pun yang diulang. Pemeriksaan kata label terselubung memakai pola leksikal disertai tinjauan makna oleh Codex, bukan penilaian manusia independen. Sampel lengkap berikut disediakan untuk pemeriksaan pemilik.

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
- **34 uji pemeriksa lolos**, termasuk data rusak: ID/sumber bocor, JSON rusak, roster, aturan neutral, kuota, syarat kasus, kemiripan, duplikat intent, konteks berulang, kekurangan setiap penanda santai, frekuensi catatan, catat pada intent, ambang bela 3%/4%, label terselubung, serta perubahan anotasi yang dilarang. Cek pola intent memakai manifest hasil tinjauan ditambah penanda teks.

Jalankan ulang dari akar repo:

```powershell
venv\Scripts\python.exe ai_2_dataset_baru\data\tambahan_2026-10-27\cek_tambahan.py
venv\Scripts\python.exe ai_2_dataset_baru\data\tambahan_2026-10-27\alat\uji_pemeriksa.py
```

## Batas pekerjaan dan kondisi repo

Dataset lama dan kedua alat asli sama byte per byte dengan hash awal. Tidak ada training, perubahan notebook oleh alur ini, perubahan di Games, commit, atau push. Plan di Games hanya dibaca sebagai instruksi. Status Git awal sudah memuat perubahan dataset/notebook milik pengguna; detail dan hash disimpan di `alat/kondisi_awal.json`.

Windows tidak dapat menyimpan `laporan.md` dan `LAPORAN.md` sebagai dua file berbeda dalam folder yang sama. Karena itu hasil impor ditempatkan di `alat/laporan_impor.md`, sedangkan laporan akhir memakai nama `LAPORAN.md` ini.

**Pekerjaan notebook oleh pemilik:** pengguna menyatakan sedang menyiapkan integrasi tambahan khusus train dan uji tambahan pada tiga notebook. Perubahan hash notebook terhadap putaran pertama dicatat di hasil cek; pekerjaan revisi data ini tidak menulis, menimpa, atau memulihkannya. Dataset lama dan alat asli tetap cocok dengan hash awal.

Hash keluaran untuk pemeriksaan integritas:

| File | SHA-256 |
| --- | --- |
| dataset_target_tambahan.csv | `0680f133a845429c70bbaaa02455cea3848b85c8b3eb902bcc85021895384b65` |
| dataset_intent_tambahan.csv | `9a161261cba74c94f18ae6743c5a4daed1464d332e2901641b1fd11d6d54cc6f` |

## Revisi 1 — ukuran sebelum dan sesudah

| Ukuran | Data lama | Sebelum revisi | Sesudah revisi | Syarat |
| --- | ---: | ---: | ---: | --- |
| Konteks unik | 97.89% | 74.91% | **100.00%** | ≥95% |
| Pemakaian maksimum teks konteks | 8× | 25× | **1×** | ≤2× |
| catatan / 1.000 kata | 0.000 | 12.194 | **0.000** | ≤1 |
| sih / 1.000 kata | 3.712 | 0.168 | **4.498** | ≥1.856 |
| kok / 1.000 kata | 3.395 | 0.280 | **4.783** | ≥1.698 |
| dong / 1.000 kata | 0.717 | 0.000 | **2.391** | ≥0.359 |
| nih / 1.000 kata | 2.278 | 0.000 | **6.035** | ≥1.139 |
| Intent memuat catat | 0.37% | 7% | **0%** | 0 |
| Intent memuat bela/pembelaan/membela | 2.19% | 5.00% | **0.00%** | ≤3% |
| Teks baru terdeteksi label terselubung | — | 2 | **0** | 0 |

Konteks unik/repetisi dihitung dengan casefold dan normalisasi spasi. Kata dihitung memakai `\b\w+\b`; penyebut frekuensi partikel dan catatan adalah seluruh kata konteks + utama. Intent catat mencakup bentuk seperti dicatat/catatanku; bela/pembelaan/membela dihitung sebagai kata utuh. Nilai data lama dihitung ulang dari CSV aktual dengan definisi yang sama, sehingga ukuran bela dapat berbeda dari taksiran awal pada plan.

Semua ambang ini kini diperiksa oleh cek_tambahan.py; pelanggaran menghasilkan exit code 1. Struktur/anotasi juga dibandingkan terhadap snapshot sebelum revisi, bukan hanya diperiksa validitasnya.

## 10 sampel konteks hasil revisi

Sepuluh pesan konteks dipilih secara acak berstrata (seed 20261028). Posisi, pengirim, intent, target, dan bukti tetap sama. Sesi lengkap lain tersedia dalam 20 sampel target setelah bagian ini.

### Konteks 1: reference_start — `r002872_v02`, pesan 9

Pengirim **Atika** · intent **neutral** · target **[]**

Sebelum: perkiraan panjang jeda belum akan ditambahkan.

Sesudah: **ya udah, urutan waktunya aja yang bisa dipakai sekarang.**

### Konteks 2: reference_start — `r002405_v02`, pesan 12

Pengirim **Marsha** · intent **neutral** · target **[]**

Sebelum: oke, sekarang penggunaan kata tadi bisa dibaca lebih jelas.

Sesudah: **oke, lanjut ke cerita yang disampaikan pada awal pembahasan.**

### Konteks 3: ambiguous — `r000226_v02`, pesan 1

Pengirim **Kirana** · intent **neutral** · target **Raksa:neutral, Aksara:neutral**

Sebelum: Raksa dan Aksara masing-masing berhenti mengetik saat topik vote muncul.

Sesudah: **Raksa juga Aksara berhenti mengetik pas sesi vote dimulai.**

### Konteks 4: witness — `r002961_v02`, pesan 1

Pengirim **Yudhis** · intent **neutral** · target **Rizal:neutral**

Sebelum: ada ringkasan pesan Rizal di catatanku; isinya bisa kita baca bersama.

Sesudah: **Rizal baru mengirim lanjutan setelah pesan pertama.**

### Konteks 5: mixed_relations — `r002985_v02`, pesan 2

Pengirim **Delima** · intent **neutral** · target **[]**

Sebelum: bagian klaim dan bagian hasilnya sudah terpisah di catatan.

Sesudah: **gw pengin tahu alasan di balik masing-masing pilihan.**

### Konteks 6: short_history_1 — `r003192_v02`, pesan 1

Pengirim **Zahira** · intent **offend** · target **Ferdi:offend**

Sebelum: yang kucurigai Ferdi; tidak menjawab pertanyaan aksi itu aneh.

Sesudah: **pilihanku tetap vote Ferdi, ada bagian alibinya yang ngarang.**

### Konteks 7: self — `r000874_v02`, pesan 1

Pengirim **Tirta** · intent **neutral** · target **Kautsar:neutral, Najwa:neutral**

Sebelum: Kautsar memakai kata Guard pada pesannya, Najwa hanya menulis nama role.

Sesudah: **Kautsar sama Najwa kirim klaim pas diskusi baru kebuka.**

### Konteks 8: second_person — `r005051_v02`, pesan 1

Pengirim **Cantika** · intent **neutral** · target **Rasyid:neutral**

Sebelum: Rasyid, bisa komentari penjelasan yang kuberikan soal urutan malam?

Sesudah: **Rasyid, bisa tanggapi penjelasan waktu aksiku sekarang?**

### Konteks 9: plural_reference — `r001399_v02`, pesan 1

Pengirim **Sakti** · intent **neutral** · target **Najwa:neutral, Isna:neutral**

Sebelum: yang belum selesai menjelaskan urutan chat ada dua, Isna dan Najwa.

Sesudah: **dua orang yang masih cerita soal malam tadi itu Isna dan Najwa.**

### Konteks 10: agreement — `r000439_v02`, pesan 1

Pengirim **Nayla** · intent **defend** · target **Raksa:defend**

Sebelum: Raksa aman, keterlambatan chatnya masih masuk akal.

Sesudah: **Raksa bukan pelakunya menurutku, jeda chat itu bukan bukti.**


## 20 sampel target untuk diperiksa

Pemilihan acak berstrata, seed **20261027**: satu sesi tiap kasus, ditambah satu lagi untuk enam kasus prioritas 1. Kasus prioritas 1 selain mixed_relations menampilkan satu defend dan satu label lainnya; stratum defend witness dipilih dari bantahan yang membela pengirim. Riwayat ditampilkan utuh agar acuan dan label konteks bisa diperiksa. Format relasi: pemain:relasi.

### 1. ambiguous — `r002913_v02`

Roster: Ghina, Savira, Salsabila, Tsania, Asih. Sumber CSV baris 2913.

| Posisi | Pengirim | Teks | Intent | Target |
| --- | --- | --- | --- | --- |
| Riwayat 1 | Asih | nih, Salsabila dan Ghina dua-duanya lagi cerita soal malam kedua. | neutral | Ghina:neutral, Salsabila:neutral |
| Riwayat 2 | Savira | kalau soal dua klaim itu, aku belum kasih kesimpulan. | neutral | Ghina:neutral, Salsabila:neutral |
| **Utama** | **Tsania** | **gerak-geriknya bikin ragu, dia seperti sudah tahu siapa yang bakal disandera.** | **offend** | **tidak_diketahui:offend** |

### 2. rhetorical_question — `r001720_v02`

Roster: Rahma, Kirana, Nayla, Erlina, Ayuning. Sumber CSV baris 1720.

| Posisi | Pengirim | Teks | Intent | Target |
| --- | --- | --- | --- | --- |
| Riwayat 1 | Ayuning | gw baru selesai cerita tentang tampilan saat fase berubah. | neutral | [] |
| **Utama** | **Kirana** | **kamu mengira perubahan target mendadak itu wajar? Buatku jelas mencurigakan.** | **offend** | **Ayuning:offend** |

### 3. self — `r000787_v02`

Roster: Naura, Anindya, Feby, Aisyah, Zakia. Sumber CSV baris 787.

| Posisi | Pengirim | Teks | Intent | Target |
| --- | --- | --- | --- | --- |
| Riwayat 1 | Anindya | Naura sama Aisyah baru jawab setelah sama-sama diam sebentar. | neutral | Naura:neutral, Aisyah:neutral |
| Riwayat 2 | Zakia | yang belum cerita soal dirinya boleh lanjut sekarang. | neutral | [] |
| **Utama** | **Feby** | **aku tadi cuma baca ulang chat, bukan sedang menyusun aksi Hitman. Jangan vote aku.** | **defend** | **Feby:defend** |

### 4. interruption — `r002058_v02`

Roster: Nadya, Haris, Izza, Amel, Khansa. Sumber CSV baris 2058.

| Posisi | Pengirim | Teks | Intent | Target |
| --- | --- | --- | --- | --- |
| Riwayat 1 | Haris | gw belum menanggapi, baru selesai baca pesan Khansa. | neutral | Khansa:neutral |
| Riwayat 2 | Nadya | semuanya, tersisa delapan belas detik buat kalimat terakhir. | neutral | [] |
| Riwayat 3 | Izza | oke kok, waktunya belum habis, lanjutkan saja obrolannya. | neutral | [] |
| **Utama** | **Amel** | **oke timer lanjut, aku akan vote Khansa. Cerita soal Guard-nya kedengaran ngarang.** | **offend** | **Khansa:offend** |

### 5. plural_reference — `r000285_v02`

Roster: Febi, Khansa, Cahya, Yasmin, Hafiz. Sumber CSV baris 285.

| Posisi | Pengirim | Teks | Intent | Target |
| --- | --- | --- | --- | --- |
| Riwayat 1 | Khansa | yang belum mengaku role ada Yasmin sama Hafiz, keduanya masih ngetik. | neutral | Hafiz:neutral, Yasmin:neutral |
| Riwayat 2 | Cahya | kedua pemain itu masih jadi bahasan, aku belum pindah topik. | neutral | Hafiz:neutral, Yasmin:neutral |
| **Utama** | **Febi** | **Cahya, jangan termakan cerita mereka berdua; klaimnya terdengar palsu.** | **offend** | **Hafiz:offend, Yasmin:offend** |

### 6. ambiguous — `r000425_v02`

Roster: Nadira, Kirana, Amel, Zulfikar, Pandu. Sumber CSV baris 425.

| Posisi | Pengirim | Teks | Intent | Target |
| --- | --- | --- | --- | --- |
| Riwayat 1 | Amel | yang barusan nanya hasil malam itu Kirana sama Pandu. | neutral | Kirana:neutral, Pandu:neutral |
| Riwayat 2 | Nadira | aku masih menunggu tambahan dari dua orang tadi. | neutral | Kirana:neutral, Pandu:neutral |
| **Utama** | **Zulfikar** | **aku tetap bela dia; mengulang pertanyaan bukan berarti sedang mengalihkan isu.** | **defend** | **tidak_diketahui:defend** |

### 7. short_history_1 — `r004605_v02`

Roster: Renata, Rahma, Nirmala, Luthfan, Asih. Sumber CSV baris 4605.

| Posisi | Pengirim | Teks | Intent | Target |
| --- | --- | --- | --- | --- |
| Riwayat 1 | Luthfan | gw Spy, nanti sekalian cerita kapan pakai Guard. | neutral | [] |
| **Utama** | **Asih** | **Luthfan yang baru klaim itu sus, alasannya terlalu dibuat-buat.** | **offend** | **Luthfan:offend** |

### 8. self — `r003006_v02`

Roster: Mahdi, Vanya, Ferdi, Tisna, Zahira. Sumber CSV baris 3006.

| Posisi | Pengirim | Teks | Intent | Target |
| --- | --- | --- | --- | --- |
| Riwayat 1 | Zahira | Tisna serta Ferdi sama-sama minta hasil skill dibahas lebih dulu. | neutral | Ferdi:neutral, Tisna:neutral |
| Riwayat 2 | Vanya | di layar sini obrolannya masih terus jalan. | neutral | [] |
| **Utama** | **Mahdi** | **tetapkan saja aku sebagai pilihan vote terakhir, aku sudah pasrah.** | **offend** | **Mahdi:offend** |

### 9. mixed_relations — `r001945_v02`

Roster: Embun, Erlina, Isna, Marsha, Pandu. Sumber CSV baris 1945.

| Posisi | Pengirim | Teks | Intent | Target |
| --- | --- | --- | --- | --- |
| Riwayat 1 | Erlina | gw lihat Isna menjelaskan bagian waktunya di akhir kalimat. | neutral | Isna:neutral |
| Riwayat 2 | Embun | gw pengin dengar dua sisi penjelasan sebelum putuskan apa pun. | neutral | [] |
| **Utama** | **Marsha** | **dia nggak pantas dituduh setelah urutannya jelas; Pandu yang menurutku sengaja merusak urutan itu.** | **offend** | **Isna:defend, Pandu:offend** |

### 10. witness — `r003243_v02`

Roster: Nayla, Utari, Syauqi, Naufala, Rayhan. Sumber CSV baris 3243.

| Posisi | Pengirim | Teks | Intent | Target |
| --- | --- | --- | --- | --- |
| Riwayat 1 | Utari | gw sudah intip Nayla, hasilnya justru Hitman. | offend | Nayla:offend |
| Riwayat 2 | Syauqi | semuanya boleh kasih pendapat, asal kalimatnya selesai dulu. | neutral | [] |
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
| Riwayat 1 | Syauqi | Izza, kamu sudah pakai skill atau baru mau menyebut role? | neutral | Izza:neutral |
| **Utama** | **Izza** | **jawabanku singkat: aku Stalker dan sudah menggunakan Peek sekali.** | **neutral** | **Syauqi:neutral** |

### 13. multiple_targets — `r003245_v02`

Roster: Thalia, Ghani, Kinanti, Tania, Bagaskara. Sumber CSV baris 3245.

| Posisi | Pengirim | Teks | Intent | Target |
| --- | --- | --- | --- | --- |
| Riwayat 1 | Tania | Kinanti juga Bagaskara sempat pindah pilihan sebelum vote dikunci. | neutral | Kinanti:neutral, Bagaskara:neutral |
| **Utama** | **Ghani** | **jangan seret Kinanti maupun Bagaskara jadi pelaku hanya karena chatnya belum lengkap.** | **defend** | **Kinanti:defend, Bagaskara:defend** |

### 14. reference_start — `r001824_v02`

Roster: Jauhar, Bagaskara, Kinanti, Khalisa, Rasyid. Sumber CSV baris 1824.

| Posisi | Pengirim | Teks | Intent | Target |
| --- | --- | --- | --- | --- |
| Riwayat 1 | Bagaskara | Kinanti baru ngaku Stalker, belum bilang siapa yang di-Peek. | neutral | Kinanti:neutral |
| Riwayat 2 | Rasyid | buat semuanya, klaim sama hasil nanti kirim satu pesan atau pisah? | neutral | [] |
| Riwayat 3 | Jauhar | bisa dipisah, asal hasilnya nyambung sama malam yang disebut. | neutral | [] |
| Riwayat 4 | Khalisa | aku lebih gampang baca kalau dua pesan pendek sih. | neutral | [] |
| Riwayat 5 | Bagaskara | gw biasanya taruh nomor malam dulu baru hasil. | neutral | [] |
| Riwayat 6 | Rasyid | boleh juga, yang penting teksnya lengkap. | neutral | [] |
| Riwayat 7 | Jauhar | ini masih sesi diskusi kok, belum kehabisan waktu. | neutral | [] |
| Riwayat 8 | Khalisa | kalau ada hasil baru, kirim setelah klaimnya dong. | neutral | [] |
| Riwayat 9 | Bagaskara | jangan campur laporan malam pertama dan kedua jadi satu. | neutral | [] |
| Riwayat 10 | Rasyid | iya, aku tadi kebalik waktu baca urutan di atas. | neutral | [] |
| Riwayat 11 | Jauhar | sekarang bagian terakhir masih pengakuan role aja nih. | neutral | [] |
| Riwayat 12 | Khalisa | lanjut, hasil atau tanggapannya boleh dikirim. | neutral | [] |
| **Utama** | **Khalisa** | **aku kembali ke klaim di awal: dia ngarang, karena dua versinya nggak mungkin sama-sama benar.** | **offend** | **Kinanti:offend** |

### 15. witness — `r000996_v02`

Roster: Salma, Tania, Anindya, Larasati, Rasyid. Sumber CSV baris 996.

| Posisi | Pengirim | Teks | Intent | Target |
| --- | --- | --- | --- | --- |
| Riwayat 1 | Salma | gw lihat Tania menjelaskan bagian waktunya di akhir kalimat. | neutral | Tania:neutral |
| Riwayat 2 | Anindya | pesan yang tadi masuk masih terbaca di layar grup. | neutral | [] |
| **Utama** | **Rasyid** | **aku setuju poin Salma: vote Tania, ceritanya soal Peek bertentangan dengan ucapannya sendiri.** | **offend** | **Tania:offend** |

### 16. mixed_relations — `r002801_v02`

Roster: Ajeng, Delima, Rosita, Sabrina, Nadhif. Sumber CSV baris 2801.

| Posisi | Pengirim | Teks | Intent | Target |
| --- | --- | --- | --- | --- |
| Riwayat 1 | Sabrina | Delima baru mengirim lanjutan setelah pesan pertama. | neutral | Delima:neutral |
| Riwayat 2 | Ajeng | buat grup, kita pakai nomor malam yang sama waktu ngobrol. | neutral | [] |
| **Utama** | **Rosita** | **dia aman dari Peek yang kulakukan, tetapi Nadhif mesti diperiksa sebagai calon Hitman.** | **offend** | **Delima:defend, Nadhif:offend** |

### 17. second_person — `r001582_v02`

Roster: Salma, Arum, Zafran, Salsabila, Yasmin. Sumber CSV baris 1582.

| Posisi | Pengirim | Teks | Intent | Target |
| --- | --- | --- | --- | --- |
| Riwayat 1 | Zafran | aku nanya pendapat kamu soal role-ku nih, Salsabila. | neutral | Salsabila:neutral |
| Riwayat 2 | Salma | sebentar, jam di game menunjukkan sisa lima belas detik. | neutral | [] |
| Riwayat 3 | Zafran | Salsabila, boleh lanjut tanggapi klaimku setelah selingan waktu tadi. | neutral | Salsabila:neutral |
| **Utama** | **Salsabila** | **kamu yang menyapa aku tadi sepertinya ngarang. Aku tidak percaya klaim Stalker-mu.** | **offend** | **Zafran:offend** |

### 18. short_history_1 — `r003610_v02`

Roster: Almira, Kemal, Renata, Marsha, Isna. Sumber CSV baris 3610.

| Posisi | Pengirim | Teks | Intent | Target |
| --- | --- | --- | --- | --- |
| Riwayat 1 | Almira | yang gw curigai Isna, kok terus menghindari pertanyaan aksi? | offend | Isna:offend |
| **Utama** | **Isna** | **yang ditulis tadi cuma potongan ucapanku. Aku nggak bersalah.** | **defend** | **Isna:defend** |

### 19. reference_start — `r000394_v02`

Roster: Astri, Hanif, Thalia, Yudhis, Anindya. Sumber CSV baris 394.

| Posisi | Pengirim | Teks | Intent | Target |
| --- | --- | --- | --- | --- |
| Riwayat 1 | Yudhis | Hanif cerita hasil akhirnya dulu, baru menjelaskan awal malam. | neutral | Hanif:neutral |
| Riwayat 2 | Anindya | ini ceritanya mundur ya, semuanya? | neutral | [] |
| Riwayat 3 | Astri | iya, kalimat pertama memang ringkasan akhir kejadian. | neutral | [] |
| Riwayat 4 | Thalia | gw sih tadi keburu mengira urutan kalimat sama dengan waktunya. | neutral | [] |
| Riwayat 5 | Yudhis | kata sebelumnya muncul pada bagian kedua kok. | neutral | [] |
| Riwayat 6 | Anindya | oh, berarti bagian kedua menceritakan hal yang lebih awal. | neutral | [] |
| Riwayat 7 | Astri | buat grup, lihat kata sebelum dan sesudahnya juga dong. | neutral | [] |
| Riwayat 8 | Thalia | kalau cuma nama skillnya yang dibaca, waktunya bisa tertukar. | neutral | [] |
| Riwayat 9 | Yudhis | aku sudah baca dua kalimatnya sekaligus sekarang. | neutral | [] |
| Riwayat 10 | Anindya | nomor malam di masing-masing bagian masih terlihat. | neutral | [] |
| Riwayat 11 | Astri | nah, urutan kejadian mulai nyambung nih. | neutral | [] |
| Riwayat 12 | Thalia | oke, silakan lanjut pendapat soal cerita malam itu. | neutral | [] |
| **Utama** | **Thalia** | **pembahasan panjang ini tidak membuat dia layak divote. Aku masih percaya dia warga.** | **defend** | **Hanif:defend** |

### 20. agreement — `r001995_v02`

Roster: Mahesa, Asih, Dyah, Ayuning, Habib. Sumber CSV baris 1995.

| Posisi | Pengirim | Teks | Intent | Target |
| --- | --- | --- | --- | --- |
| Riwayat 1 | Ayuning | gw curiga Mahesa, klaim role-nya seperti dibuat-buat. | offend | Mahesa:offend |
| Riwayat 2 | Habib | eh grup, sesi memilih belum terbuka, masih ngobrol. | neutral | [] |
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
| 19 | peek_membersihkan | hasil peek semalam buat si L: Civilian, jangan salah vote nih | defend |
| 38 | peek_membersihkan | peek ke Banyu selesai, hasilnya bukan Hitman kok, jadi tahan vote itu | defend |
| 50 | peek_membersihkan | gw intip Haikal semalam dan yang kebaca warga biasa, stop tuduh dia | defend |
| 36 | peek_membersihkan | si U terbaca bukan Hitman, itu laporan hasil Peek-ku ronde ini | defend |
| 96 | klaim_murni | gw warga biasa, cuma mau melengkapi daftar klaim | neutral |
| 62 | klaim_pembelaan | aku Spy, jadi tuduhan bahwa aku menyandera orang itu tidak benar | defend |
| 68 | klaim_pembelaan | aku Spy, jangan desak aku memberikan hasil pengintaian palsu | defend |
| 56 | klaim_pembelaan | aku bukan Hitman, aku warga biasa; itu sebabnya nggak ada skill buat kulaporkan | defend |
| 64 | klaim_pembelaan | role gw Stalker, tolong jangan eksekusi gw dari dugaan semata | defend |
| 88 | klaim_murni | role gw Civilian, itu info yang mau kutulis dulu | neutral |

## Pemakaian berikutnya

Integrasi ke bagian train dan penyisihan uji tambahan dikerjakan pemilik proyek pada notebook. Pekerjaan revisi ini tidak mengubah dataset lama, pembagian test, atau menjalankan evaluasi/training model.
