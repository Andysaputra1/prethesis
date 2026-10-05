# Fuzzy logic: menilai petunjuk yang tidak hitam-putih

Sumber utama: [npc_fuzzy.ipynb](../npc_fuzzy.ipynb). Versi yang dipakai game: [otak_fuzzy.py](../../../../Games/backend/services/npc_brain/generated/otak_fuzzy.py).

## 1. Bayangkan menilai suhu air

Air tidak selalu hanya “dingin” atau “panas”. Air hangat bisa agak dekat ke sedang dan agak dekat ke panas. Fuzzy logic memakai ide serupa untuk petunjuk permainan.

Misalnya tekanan terhadap Budi sebesar 0,65. Kita tidak harus membuat batas kaku bahwa 0,64 aman dan 0,65 langsung sangat mencurigakan. Nilai itu dapat mempunyai derajat keanggotaan **sedang 0,5** dan **tinggi 0,5** sekaligus.

Derajat keanggotaan bukan probabilitas role. “Tekanan tinggi sebesar 0,5” tidak berarti Budi 50% Hitman; itu hanya seberapa cocok angka tekanan dengan kategori tinggi.

## 2. Fuzzy yang mana?

Di Games ada [fuzzy_service.py](../../../../Games/backend/services/fuzzy_service.py), yaitu jalur analisis lama dengan dua input agresivitas dan persentase diam. Panduan ini menjelaskan **otak NPC notebook**, yang memakai banyak bukti dan beberapa sistem fuzzy berjenjang.

Saat mengikuti `BrainRuntime.langkah` dalam mode fuzzy, buka `generated/otak_fuzzy.py`. Jangan memakai diagram fuzzy lama untuk menjelaskan sistem NPC ini.

## 3. Input fuzzy berasal dari mana?

`hitung_bukti` lebih dahulu membentuk tabel bukti per pemain. Contoh kolomnya:

```python
{
    "pemain": "Budi",
    "tekanan": 0.65,
    "dukungan": 0.35,
    "inkonsistensi": 0.0,
    "pengalihan": 0.5,
    # Masih ada bukti lain, status kandidat, dan dugaan sandera.
}
# Contoh input penalaran; bukan data pemain nyata.
```

Fuzzy tidak menerima chat mentah secara langsung. NLU dan memori sudah mengubah chat/vote menjadi petunjuk numerik. Karena itu salah pembacaan nama atau urutan chat dapat memengaruhi fuzzy meskipun perhitungan fuzzy berjalan benar.

## 4. Empat langkah perhitungan Mamdani

Cari `_bangun_sistem`, `_mf`, `_fuzzy_tersimpan`, dan `fuzzy`.

### Langkah A — Fuzzifikasi

Angka input 0–1 diubah menjadi keanggotaan kategori:

| Kategori | Titik pada `MF_INPUT` | Makna mudah |
| --- | --- | --- |
| Rendah | 0, 0, 0.2, 0.5 | Penuh sampai 0,2; turun menjadi nol di 0,5. |
| Sedang | 0.2, 0.5, 0.8 | Naik ke puncak di 0,5, lalu turun. |
| Tinggi | 0.5, 0.8, 1, 1 | Mulai naik setelah 0,5; penuh mulai 0,8. |

Empat titik membuat bentuk trapesium (`trapmf`). Tiga titik membuat segitiga (`trimf`). Sumbu mendatar adalah nilai input; sumbu tegak adalah keanggotaan 0–1.

Pada 0,65:

```text
sedang = (0,8 − 0,65) / (0,8 − 0,5) = 0,5
tinggi = (0,65 − 0,5) / (0,8 − 0,5) = 0,5
rendah = 0
```

`keanggotaan(x)` membantu melihat angka tersebut saat menelusuri kode.

### Langkah B — Jalankan aturan IF/AND/THEN

Contoh sistem `sosial` memakai input tekanan dan dukungan. Matriks `aturan` dibaca **baris = tekanan**, **kolom = dukungan**:

| Tekanan / Dukungan | Rendah | Sedang | Tinggi |
| --- | --- | --- | --- |
| Rendah | Rendah | Rendah | Rendah |
| Sedang | Sedang | Rendah | Rendah |
| Tinggi | Tinggi | Sedang | Sedang |

Contoh aturan: IF tekanan tinggi AND dukungan rendah THEN sosial tinggi.

Kekuatan AND adalah nilai minimum kedua keanggotaan. Jika tekanan tinggi 0,5 dan dukungan rendah 0,5, aturan menyala dengan kekuatan 0,5. Dalam satu input, beberapa aturan dapat menyala bersamaan.

`aturan_aktif(nama, a, b)` menampilkan aturan yang menyala dan kekuatannya. Berguna ketika kamu bertanya “hasil ini berasal dari aturan mana?”.

### Langkah C — Gabungkan keluaran aturan

Setiap aturan membatasi tinggi bentuk keluaran sesuai kekuatannya. Semua keluaran digabung dengan maksimum. Ini disebut agregasi.

`MF_OUTPUT` memakai segitiga:

- Rendah: [0, 15, 30].
- Sedang: [35, 50, 65].
- Tinggi: [70, 85, 100].

Output rendah tidak otomatis bernilai nol. Pusat segitiga rendah ada di 15.

### Langkah D — Defuzzifikasi

Bentuk gabungan diubah menjadi satu angka dengan **centroid**, yaitu titik keseimbangan luas bentuknya. `keluaran.defuzzify_method = "centroid"` menetapkan cara ini.

Hasil satu sistem berada pada skala 0–100. Saat masuk ke tingkat berikutnya, `nilai_kecurigaan` membaginya dengan 100 agar kembali 0–1.

## 5. Contoh hitungan yang sudah dicocokkan dengan kode

```python
fuzzy("sosial", 0.65, 0.35)  # sekitar 50.0
fuzzy("sosial", 0.80, 0.20)  # 85.0
```

Pada contoh pertama, tekanan mempunyai keanggotaan sedang/tinggi masing-masing 0,5; dukungan mempunyai rendah/sedang masing-masing 0,5. Empat kombinasi aturan menyalakan keluaran rendah, sedang, dan tinggi. Gabungannya seimbang di sekitar 50.

Pada contoh kedua, tekanan tinggi penuh dan dukungan rendah penuh menyalakan keluaran tinggi. Centroid segitiga tinggi adalah 85.

**Ini baru nilai sosial**, belum skor kecurigaan akhir, apalagi keputusan vote. Hasil nyata masih melewati bukti lain dan aturan tindakan.

## 6. Mengapa ada hierarki?

Daripada membuat satu sistem dengan sangat banyak kombinasi input, kode menggabungkan bukti sedikit demi sedikit. Cari `HIERARKI`:

```text
tekanan + dukungan                     → sosial
inkonsistensi + pengalihan              → perilaku
dituduh_korban + dorong_salah_eksekusi   → jejak
serang_bersih + klaim                   → pribadi
sosial + perilaku                       → ucapan
jejak + pribadi                        → bukti_keras
ucapan + bukti_keras                    → kecurigaan
```

Setiap panah menggunakan sistem Mamdani dua input dengan 3×3 = 9 aturan. Istilah “bukti keras” di sini adalah nama kelompok rancangan; tidak menjadikan semua dugaan di dalamnya fakta pasti.

Setelah hierarki:

```text
kecurigaan akhir = kecurigaan mentah × (1 − p_sandera)
```

Rumus ini hanya berlaku untuk pemain kandidat. Pemain yang bukan kandidat diberi nol. Misalnya skor mentah 0,80 dan dugaan sandera 0,75 menghasilkan 0,20. Tujuannya menghindari menuduh orang yang mungkin justru korban.

Kemudian `terapkan_pengetahuan` bisa menimpa hasil: Hitman yang diketahui mendapat skor 1; pemain yang diketahui bersih mendapat 0. Klaim bersih yang belum pasti diperlakukan sebagai penurunan skor, bukan otomatis fakta.

## 7. Dari kecurigaan menjadi tindakan

Kecurigaan menjawab “siapa yang patut dicurigai?”. Prioritas tindakan menjawab “apa yang sebaiknya dilakukan sekarang?”. Keduanya memakai perhitungan berbeda.

### Chat

`calon_chat` membuat tindakan yang relevan: membela diri, menjawab pertanyaan, menuduh, membela orang, dan sebagainya. `keputusan_chat` memberi setiap calon skor fuzzy sesuai `SISTEM_KEPUTUSAN`.

Calon diurutkan menurut skor, prioritas aksi saat seri, lalu nama target. Jika tidak ada calon atau skor terbaik di bawah **AMBANG_CHAT = 40**, bot menunggu. `izin_chat` diperiksa lebih dahulu. Fakta Peek dapat melewati pemilihan chat biasa melalui `chat_pasti`.

### Vote warga

`keputusan_vote` menyaring kandidat: tidak termasuk yang pasti bersih atau dugaan sandera tinggi. Lalu:

1. Hitung selisih kecurigaan kandidat teratas terhadap pesaing.
2. Gabungkan kecurigaan dan keunggulan menjadi `keyakinan_vote`.
3. Gabungkan keyakinan dan urgensi menjadi `kesiapan_vote`.
4. Skor ≥ 75 bisa memicu vote langsung; skor ≥ 45 bisa memicu vote setelah setengah fase.
5. Jika belum siap, bot menunggu, mempertimbangkan arah suara yang masuk akal, atau abstain.

Urgensi berasal dari perkiraan selisih warga bebas dan Hitman hidup. Ia bukan sekadar timer yang hampir habis. `porsi_fase` adalah ukuran waktu fase yang terpisah.

### Skill dan role Hitman

`calon_aksi` memastikan target sesuai jenis skill. `keputusan_aksi` memberi skor pada calon. Hostage/Guard/Peek memilih calon terbaik yang tersedia; Gag juga harus melewati **AMBANG_GAG = 60**.

Untuk Hitman, `fitur_hitman` dan `nilai_ancaman` menilai siapa warga yang mengancam dan siapa yang terlihat mudah dijadikan kambing hitam. Skor publik bukan role rahasia lawan. Vote Hitman memakai `keputusan_vote_hitman`, bukan rumus kesiapan vote warga di atas.

## 8. Jalur fungsi untuk dibaca berurutan

```text
putuskan
 ├─ hitung_bukti
 ├─ pengetahuan_peran
 ├─ nilai_kecurigaan → fuzzy → _fuzzy_tersimpan
 ├─ terapkan_pengetahuan (jalur warga)
 ├─ chat_pasti / keputusan_chat
 ├─ vote_pasti / keputusan_vote atau keputusan_vote_hitman
 ├─ keputusan_aksi
 └─ format_npc + siapkan_nlg
```

`SIMULASI` menyimpan sistem fuzzy; cache `_fuzzy_tersimpan` menghindari menghitung ulang input yang sama. `fuzzy` menolak input bukan angka finite atau di luar 0–1, lalu membulatkan input sampai empat desimal. Sistem simulasi bersifat mutable; runtime menyerialkan keputusan bot melalui satu pekerja.

## 9. Saat membaca hasil yang aneh

Periksa tabel bukti dahulu, lalu aturan aktif, baru ambang tindakan. Jangan menyamakan output fuzzy 85 dengan “85% pasti Hitman”. Bobot, bentuk kurva, dan ambang adalah keputusan desain yang perlu evaluasi; bukan angka yang dipelajari oleh training IndoBERT.

Audit menemukan kronologi chat dapat salah dan kalimat campuran bisa salah target. Keduanya berada sebelum fuzzy, tetapi memengaruhi hasil fuzzy. Pada pengujian yang dijalankan, 45 skenario fuzzy dan pemeriksaan khusus notebook lulus; itu tidak menghapus masalah integrasi tersebut.
