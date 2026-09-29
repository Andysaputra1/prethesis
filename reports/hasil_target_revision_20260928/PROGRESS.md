# Progress pemeriksaan hasil dataset target HOSTAGE

Status: DIHENTIKAN atas permintaan pengguna pada 28 September 2026. Jangan melanjutkan pemeriksaan/perbaikan sebelum diminta pengguna.

## Instruksi pengguna yang berlaku

- Perbaiki file HASIL langsung; jangan mengubah prompt, generator, atau aturan game.
- Sesuaikan percakapan, intent, target, dan bukti acuan dengan konteks game HOSTAGE.
- Catat progress setiap batch selesai, termasuk perbedaan antara checkpoint dan file hasil yang sudah diperbarui.

## Titik terakhir

| Tahap | Cakupan | Status |
| --- | --- | --- |
| Sudah diperbaiki dan ditulis ke file hasil | 270 percakapan: hasil copy 2.txt sampai 27.txt, serta hasil copy 78.txt | Pemeriksaan schema dan validate_session lulus 270/270 sebelum ditulis. |
| Sudah dikoreksi, masih di checkpoint | 60 percakapan: hasil copy 28.txt sampai 33.txt | Belum ditulis kembali ke folder hasil dan belum divalidasi ulang setelah koreksi. |
| Sudah dibaca, belum dikoreksi | 30 percakapan: hasil copy 34.txt sampai 36.txt | Lanjutkan koreksi dari hasil copy 34.txt. |
| Sudah dicadangkan, belum dibaca | 30 percakapan: hasil copy 37.txt sampai 39.txt | Belum diperiksa. |

Total checkpoint: 390 percakapan. Sebanyak 330 sudah mendapat pemeriksaan/koreksi isi; hanya 270 yang sudah divalidasi struktur dan ditulis kembali. Lulus struktur bukan jaminan seluruh anotasi semantik sudah sempurna atau gold hasil anotasi manusia.

- Koreksi terakhir: hasil copy 33.txt, job_id r002076_v01, indeks checkpoint 329 (berbasis 0).
- Mulai koreksi berikutnya: hasil copy 34.txt, job_id r002077_v01, indeks 330.
- Terakhir dibaca: hasil copy 36.txt, job_id r002258_v01, indeks 359.
- Awal bagian belum dibaca: hasil copy 37.txt, job_id r002265_v00, indeks 360.

## Lokasi

- Hasil aktif: ai_2_dataset_baru/data/manual_pilot_25/hasil/
- Checkpoint lengkap: reports/hasil_target_revision_20260928/working_results.json
- Cadangan file asli: reports/hasil_target_revision_20260928/original/
- Catatan penulisan 270 percakapan dan hash: reports/hasil_target_revision_20260928/status.json
- Daftar job sumber: ai_2_dataset_baru/data/manual_pilot_25/jobs.json

working_results.json adalah array berisi file, job_id, dan session. Indeks 0–269 mencakup 270 hasil yang sudah ditulis. Indeks 270–329 berisi koreksi tambahan yang belum ditulis. Indeks 330–389 masih merupakan hasil asli.

## Temuan dan perbaikan yang sudah dilakukan

- Mengganti mekanik game lain seperti task, patroli lokasi, CCTV, perbaikan kabel, dan bukti gerak pemain dengan pembahasan yang didukung game HOSTAGE.
- Gag Order membungkam chat saat siang; tidak mengacak huruf atau memotong chat sebagai efek mekanis. Diam bukan bukti pasti korban atau role tertentu.
- Spy memakai Guard; tidak melihat patroli/pergerakan. Tidak dapat Guard orang sama dua malam berturut-turut.
- Stalker memakai Peek terhadap satu pemain, satu kali tiap dua ronde. Klaim hasil skill tetap ucapan pemain, bukan fakta publik yang terverifikasi.
- Chat terkunci saat malam. Identitas korban tidak diumumkan. Zero Economy tidak memiliki uang, item belanja, atau tebusan.
- Mengganti asumsi riwayat vote privat/indikator UI yang belum dikonfirmasi dengan ajakan vote yang terlihat di chat.
- Memperbaiki target diri sendiri, nama saksi, hubungan tuduhan/pembelaan, pergantian topik, acuan ambigu, dan rantai memori 12 pesan.
- Teks pada kasus original dipertahankan; anotasi/roster yang salah diperbaiki jika diperlukan.

## Catatan file yang terus bertambah

Pada snapshot awal terdapat 27 file hasil berisi 270 percakapan. Saat bekerja, file 28–39 bertambah dan sudah dicadangkan serta dimasukkan ke checkpoint. Pada pemeriksaan terakhir, hasil copy 40.txt berisi PROMPT, bukan JSON hasil; tidak diubah dan tidak dimasukkan ke checkpoint. Status file ini bisa berubah sesudahnya. File kosong dan hasil baru setelah snapshot belum dianggap selesai.

## Langkah ketika pengguna meminta lanjut

1. Muat checkpoint dari disk, bukan memori sesi tool. Jangan membaca file 28–33 dari folder hasil sebagai versi koreksi karena versi perbaikannya baru ada di checkpoint.
2. Mulai koreksi dari indeks 330 / hasil copy 34.txt. Hasil copy 34–36 pernah dibaca tetapi belum diperbaiki.
3. Validasi semua tambahan dengan build_schemas dan validate_session dari lama/generateDataset/label_target.py, tanpa mengubah prompt/generator. Bedakan koreksi makna dari sekadar lolos validator.
4. Sebelum menulis hasil, bandingkan file aktif dengan cadangan/hash agar tidak menimpa perubahan pengguna. Jangan menimpa file yang berubah tanpa merekonsiliasi isinya.
5. Simpan checkpoint dan perbarui PROGRESS.md serta status mesin setiap selesai satu batch, mencatat job terakhir dan status validasi/penulisan.
6. Inventarisasi file baru secara terpisah. Jangan menganggap prompt atau file kosong sebagai hasil yang sudah diperiksa.
