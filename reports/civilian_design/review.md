# Review Civilian — Utility AI dan Behavior Tree

Dua notebook baru; cakupan keputusan chat Civilian. Tidak ada training ulang, panggilan LLM/API, atau pengiriman dataset. Semua notebook berhasil dijalankan berurutan dengan model lokal.

- utility_ai: notebook lengkap dieksekusi, valid, dan tabel tanpa NaN.
- utility_ai: JSON valid, target kosong None, nama baru, batas waktu/roster, dan anti-penguatan diri lulus.
- behavior_tree: notebook lengkap dieksekusi, valid, dan tabel tanpa NaN.
- behavior_tree: JSON valid, target kosong None, nama baru, batas waktu/roster, dan anti-penguatan diri lulus.
- Perbedaan metode terverifikasi: satu tuduhan AI + dua target ambigu -> Utility membela diri, BT klarifikasi.
- Jalur NLU, ekstraksi target, parameter, dan izin aksi sama pada kedua metode.
- NLU lokal intent_classifier_nb.pkl: inferensi berhasil (cek integrasi, bukan akurasi).
- NLU lokal intent_classifier_nb_optuna.pkl: inferensi berhasil (cek integrasi, bukan akurasi).
- NLU lokal intent_classifier_nb_tuned.pkl: inferensi berhasil (cek integrasi, bukan akurasi).
- NLU lokal intent_classifier_svm.pkl: inferensi berhasil (cek integrasi, bukan akurasi).
- NLU lokal intent_classifier_svm_optuna.pkl: inferensi berhasil (cek integrasi, bukan akurasi).
- NLU lokal intent_classifier_svm_tuned.pkl: inferensi berhasil (cek integrasi, bukan akurasi).
- IndoBERT lokal: inferensi CPU berhasil, local_files_only=True.
- Hash fuzzy Janice, fuzzy dataset baru, dan nlu_baru tetap sama.

## Batas hasil

Ini prototipe kebijakan, bukan strategi terbaik yang sudah terbukti. Tidak ada evaluasi win rate atau akurasi ekstraksi target pada test beranotasi. Bobot dan threshold masih pilihan desain; tekanan sosial bukan probabilitas Hitman. Resolver aturan abstain pada banyak kalimat majemuk dan kata ganti, dan masih bisa salah pada bahasa di luar pola. Voting, skill, klaim role, kontradiksi, penjadwal chat, dan pemanggilan LLM belum diintegrasikan. can_chat hanya milik AI sendiri; tidak ada pembacaan status korban pemain lain.

## Cara menjalankan

Buka notebook di ai_2_dataset_baru, gunakan kernel venv proyek, lalu Run All dari folder tersebut. Atur PLAYERS dan metadata contoh sesuai event game. Model klasifikasi sudah lokal; jangan menjalankan ulang notebook training hanya untuk mencoba kebijakan.
