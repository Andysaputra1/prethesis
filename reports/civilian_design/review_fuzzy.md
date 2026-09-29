# Review fuzzy Civilian baru

Notebook: ai_2_dataset_baru/civilian_fuzzy.ipynb.

- 24 code cell berhasil dieksekusi berurutan dengan kernel proyek.
- Lima sistem Mamdani, masing-masing dua input, sembilan aturan, dan satu output prioritas.
- Total 605 kombinasi input (5 x 11 x 11) menghasilkan skor hingga dalam 0-100 dan aturan aktif.
- Batas 0, 0.5, dan 1 tercakup; nilai invalid ditolak.
- Tes kurva pembelaan diri: pressure meningkat pada uncertainty=0 tidak menurunkan prioritas.
- Kurva high memakai plateau untuk menghilangkan penurunan aktivasi yang ditemukan saat review desain segitiga awal.
- Tes target, negasi, reply-to, diri sendiri, spam, event duplikat, ronde lama, confidence rendah, malam/tribunal/izin chat, dan field rahasia lulus.
- Simulasi membela diri, pembelaan pemain lain, tantangan target, klarifikasi, dan diam tersedia.
- NLU SVM lokal berhasil dipakai di notebook; tidak ada training atau API.
- Definisi pemuat NLU (SVM/NB/IndoBERT), ekstraksi target, perhitungan parameter, izin aksi, dan payload NLG identik dengan notebook Utility AI.
- Grafik membership diperiksa secara visual; tabel kosong tidak menampilkan NaN.
- Hash notebook lama, NLU, Utility AI, dan Behavior Tree tidak berubah.

## Batas hasil

Ini verifikasi implementasi, bukan evaluasi win rate atau akurasi target di data nyata. Titik kurva dan isi aturan masih rancangan awal. Tekanan sosial dan prioritas fuzzy bukan probabilitas Hitman. Target aturan dapat abstain atau salah pada bahasa kompleks. Voting, skill, jadwal pengiriman chat, dan generator percakapan belum dihubungkan. Civilian hanya memakai informasi publik dan izin bicara dirinya sendiri.

## Cara pakai

Buka civilian_fuzzy.ipynb dengan kernel venv dan working directory ai_2_dataset_baru, lalu Run All. Default membaca model SVM yang sudah tersimpan. Ganti MODEL_FILENAME untuk NB atau NLU_BACKEND menjadi indobert untuk classifier lokal. Setelah mengubah FUZZY_RULES atau kurva, jalankan kembali pembentukan sistem dan cell sesudahnya.
