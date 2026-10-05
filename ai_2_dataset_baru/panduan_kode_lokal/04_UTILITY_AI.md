# Utility AI: memilih tindakan yang paling berguna sekarang

Sumber utama: [npc_utility_ai.ipynb](../npc_utility_ai.ipynb). Versi game: [otak_utility.py](../../../../Games/backend/services/npc_brain/generated/otak_utility.py).

## 1. Bayangkan memilih kegiatan setelah sekolah

Kamu bisa mengerjakan PR, makan, atau bermain. Kalau besok ujian, belajar lebih berguna. Kalau sangat lapar, makan naik prioritasnya. Kegiatan yang paling berguna bergantung pada situasi.

Bot juga punya beberapa pilihan. Utility AI memberi **nilai kegunaan** pada masing-masing pilihan, lalu memilih yang terbaik jika layak dilakukan. Tidak harus selalu bicara: menunggu atau abstain juga punya nilai.

Di proyek ini ada dua tahap yang perlu dibedakan:

- Menghitung **kecurigaan/ancaman pemain**, sebagai bahan penilaian.
- Menghitung **kegunaan tindakan**, misalnya tuduh Budi atau bela diri.

Pemain paling mencurigakan tidak otomatis membuat menuduh menjadi tindakan terbaik jika bot perlu menjawab pertanyaan atau belum boleh chat.

## 2. Peta fungsi

| Fungsi/konstanta | Kerjanya | Dipakai saat |
| --- | --- | --- |
| `hitung_bukti` | Menyusun petunjuk tiap pemain dari memori. | Awal setiap keputusan. |
| `BOBOT_BUKTI` | Menetapkan kekuatan relatif setiap jenis petunjuk. | Menghitung kecurigaan. |
| `nilai_kecurigaan` | Menggabungkan bukti dengan rumus noisy-OR. | Menilai kandidat warga dan citra publik. |
| `kurva_linear` / `kurva_logistik` | Mengubah besaran fitur menjadi nilai pertimbangan 0–1. | Menilai tindakan. |
| `PERTIMBANGAN` | Daftar bobot dan kurva untuk tiap jenis tindakan. | Chat dan skill. |
| `skor_iaus` | Menggabungkan beberapa pertimbangan. | Menghitung kegunaan akhir satu calon. |
| `_nilai_calon` | Mengisi skor seluruh calon. | Sebelum memilih tindakan. |
| `keputusan_chat` / `keputusan_vote` / `keputusan_aksi` | Memilih calon sesuai izin, waktu, dan pembanding. | Menghasilkan rencana. |
| `putuskan` | Menyatukan semua langkah. | Dipanggil runtime game. |

## 3. Menghitung kecurigaan dengan noisy-OR

Bayangkan beberapa lampu petunjuk. Satu petunjuk belum tentu kuat, tetapi beberapa petunjuk dapat saling menambah kecurigaan. Kode menggunakan bentuk:

```text
komponen_j = bobot_j × nilai_bukti_j
kecurigaan mentah = 1 − perkalian(1 − komponen_j)
```

Bobot dalam kode saat ini:

| Petunjuk | Bobot |
| --- | --- |
| Dituduh korban | 0,75 |
| Mendorong salah eksekusi | 0,65 |
| Klaim bermasalah | 0,60 |
| Menyerang pemain bersih | 0,50 |
| Tekanan | 0,40 |
| Pengalihan | 0,30 |
| Inkonsistensi | 0,30 |

Dukungan mengurangi komponen tekanan:

```text
komponen tekanan *= (1 − 0,7 × dukungan)
```

Contoh buatan yang mudah dihitung: tekanan 0,5 tanpa dukungan, klaim bermasalah 0,5, bukti lain nol.

```text
komponen tekanan = 0,40 × 0,5 = 0,20
komponen klaim   = 0,60 × 0,5 = 0,30
mentah          = 1 − (1 − 0,20)(1 − 0,30)
                = 1 − 0,8 × 0,7
                = 0,44
```

Jika `p_sandera=0.25`, skor kandidat menjadi `0.44 × (1 − 0.25) = 0.33`. Setelah itu, `terapkan_pengetahuan` dapat menimpa skor dengan fakta Peek/pemain bersih atau menurunkannya karena klaim bersih.

“Noisy-OR” adalah bentuk penggabungan bukti yang dipakai kode. Karena bobot dan bukti dirancang manual serta bisa saling berkaitan, hasil 0,44 tidak boleh langsung disebut probabilitas terkalibrasi 44% Hitman.

## 4. Apa itu consideration atau pertimbangan?

Untuk menuduh, bot bisa menilai:

- Seberapa besar kecurigaan target?
- Seberapa unggul target itu dibanding tersangka lain?
- Seberapa banyak informasi yang tersedia?

Masing-masing jawaban dijadikan angka 0–1. Angka-angka itulah consideration.

`PERTIMBANGAN["tuduh"]` memakai:

```python
{
    "kecurigaan": kurva_logistik(input_kecurigaan, 0.45, 12),
    "keunggulan": kurva_linear(input_keunggulan, 0.5, 0.5),
    "volume info": kurva_linear(input_volume_info, 0.4, 0.6),
}
```

Ini penulisan ulang agar mudah dibaca; di kode nilai diambil dari dictionary `i`. Dua consideration terakhir sengaja punya nilai dasar 0,5 dan 0,6. Jadi tidak unggul/minim info mengurangi kegunaan, tetapi tidak otomatis membuatnya nol.

## 5. Dua bentuk kurva yang dipakai

### Kurva linear

`kurva_linear(x, kemiringan, awal)` menghitung:

```text
nilai = clip(awal + kemiringan × x, 0, 1)
```

`clip` berarti potong hasil agar tetap antara 0 dan 1. Contoh `kurva_linear(0.4, 0.5, 0.5) = 0.7`.

### Kurva logistik

`kurva_logistik(x, tengah, curam)` membentuk kurva S:

```text
nilai = 1 / (1 + exp(−curam × (x − tengah)))
```

Pada `x=tengah`, hasilnya 0,5. Di bawah titik itu hasil makin kecil; di atasnya makin besar. `curam` menentukan seberapa tajam perubahan di sekitar titik tengah.

Contohnya, ambang tengah 0,45 membuat nilai kecurigaan di sekitar 0,45 menjadi daerah perubahan penting. Ini kurva pemetaan, bukan proses training baru.

## 6. Menggabungkan pertimbangan dengan IAUS

`skor_iaus` mengalikan pertimbangan setelah memberi kompensasi. Alasannya: mengalikan banyak angka di bawah 1 dapat membuat tindakan dengan lebih banyak pertimbangan mendapat skor sangat kecil.

Kode menghitung untuk n pertimbangan:

```text
m = 1 − 1/n
nilai_diselaraskan = x + (1 − x) × m × x
skor = bobot_tindakan × perkalian(nilai_diselaraskan)
```

Contoh yang sudah dijalankan langsung dari fungsi:

| Calon | Pertimbangan setelah kurva | Sesudah kompensasi, n=2 | Skor, bobot=1 |
| --- | --- | --- | --- |
| A | 0,8 dan 0,6 | 0,88 dan 0,72 | 0,6336 |
| B | 0,7 dan 0,7 | 0,805 dan 0,805 | 0,648025 |

B unggul tipis. Ini contoh matematika fungsi, bukan hasil lengkap tindakan tertentu. Untuk skor tindakan nyata, jalankan kurvanya dan bobot `PERTIMBANGAN` dahulu.

Jika salah satu pertimbangan nol, hasil perkalian tetap nol. Kompensasi tidak menghidupkan tindakan yang punya syarat bernilai nol. Bobot tindakan bisa lebih dari 1; karena itu **skor utility akhir tidak harus selalu dibatasi 0–1**, walaupun setiap nilai pertimbangan berada pada rentang tersebut.

## 7. Memilih chat

`keputusan_chat` melakukan:

1. Cek `izin_chat`. Jika tidak boleh, hasilnya tunggu.
2. Ambil daftar calon dari `calon_chat`.
3. `_nilai_calon` membaca konfigurasi pertimbangan tiap aksi dan menghitung utility.
4. Urutkan skor tertinggi; saat seri gunakan `URUTAN_AKSI` dan nama target.
5. Bandingkan dengan **UTILITAS_TUNGGU = 0.35**.
6. Jika skor terbaik ≤ 0,35, bot menunggu. Jika lebih tinggi, pilih calon itu.

Dengan kata lain, “ada calon tindakan” tidak cukup. Tindakan itu harus lebih berguna daripada diam. `chat_pasti` untuk mengungkap fakta Hitman dari pengetahuan bot dapat mengambil jalur prioritas sebelum penilaian biasa.

Contoh situasi: Budi agak mencurigakan, tetapi Nara sedang dituduh langsung. Daftar calon dapat memuat tuduh Budi dan bela diri. Kurva serta bobot masing-masing menentukan pilihan; jangan langsung menyimpulkan skor kecurigaan Budi adalah skor utility tuduh Budi.

## 8. Memilih vote warga

`keputusan_vote` membandingkan semua kandidat yang layak dengan abstain. Pertimbangannya:

- Kecurigaan kandidat.
- Seberapa kecil dugaan bahwa ia sandera.
- Dukungan suara yang sudah masuk.
- Keunggulan terhadap kandidat lain.

Nilai abstain:

```text
abstain = 0,15 + 0,5 × (1 − urgensi)
```

Saat urgensi rendah, abstain lebih bernilai: salah eksekusi juga berbahaya. Saat urgensi tinggi, biaya menunggu makin besar.

Jika kandidat menang atas abstain, bot tetap memperhatikan waktu: utility ≥ **0,85** boleh vote langsung; jika belum setinggi itu, tunggu sampai minimal separuh fase. Sebelum separuh fase hasil bisa “tunggu”; setelahnya bisa “abstain”. Keduanya tidak mengirim vote, tetapi alasan dan waktunya berbeda.

Fakta pasti Hitman dapat masuk lewat `vote_pasti`. Vote Hitman memakai fungsi strategi bersama `keputusan_vote_hitman`, bukan pembanding abstain warga ini.

## 9. Memilih skill dan menjalankan role Hitman

`calon_aksi` lebih dahulu menyaring target sesuai kemampuan, hidup/tidak, rekan, riwayat Guard, dan pengetahuan yang relevan.

`keputusan_aksi` memberi utility pada kandidat. Hostage, Guard, dan Peek memilih yang terbaik jika ada. Gag disimpan jika skor terbaik di bawah **AMBANG_GAG_UTILITAS = 0.55**.

Hitman mempunyai penilaian `ancaman` dan `kambing_hitam`. Ancaman memakai noisy-OR atas fitur seperti menuduh saya, klaim role, dan pengaruh, lalu disesuaikan kredibilitas. Kambing hitam memakai IAUS atas kecurigaan publik, dukungan suara, dan dugaan bukan sandera. Ini tujuan strategis Hitman, bukan bot warga yang sedang mencari kebenaran role.

## 10. Cara menelusuri satu keputusan

Buka `putuskan` → lihat `tabel` → lihat `rencana_chat` → buka `jejak_chat`.

Pada utility, jejak mencatat **pertimbangan** dan **utilitas**. Cocokkan nama aksi dengan `PERTIMBANGAN`, lalu hitung ulang nilai kurvanya. Jika skor terasa salah, periksa secara berurutan: bukti, kurva, bobot, penggabungan IAUS, pembanding diam/abstain, dan izin.

Bobot bukan hasil training otomatis. Nilai saat ini adalah rancangan yang perlu evaluasi gameplay. Kesalahan target NLU atau memori yang ditemukan audit juga berlaku pada metode ini; ia tidak dapat memperbaiki fakta masukan yang sudah salah hanya dengan rumus utility.
