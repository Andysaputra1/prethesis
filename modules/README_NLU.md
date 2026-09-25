# Alur modul NLU

Modul utama: `nlu_training.py`. Notebook pengguna: `ai_2_dataset_baru/ai_1_nlu_v3_600.ipynb`.

## Urutan pemrosesan

1. `load_clean_nlu_dataset` dari `nlu_eda.py` membersihkan data.
2. `_split_dataset` membagi train/test secara stratified (seed 42).
3. Baseline melatih parameter tetap; Grid Search mencoba semua kombinasi;
   Optuna memilih kandidat menggunakan TPE, default 50 trial.
4. Pencarian hyperparameter memakai macro-F1 cross-validation pada train.
5. Estimator terpilih dilatih pada train dan dievaluasi pada test.
6. Model serta hasil evaluasi dikembalikan ke notebook untuk ditampilkan.

## Fungsi publik

| Fungsi | Metode |
| --- | --- |
| `train_svm` / `train_naive_bayes` | Baseline |
| `train_svm_tuned` / `train_naive_bayes_tuned` | Grid Search; seluruh pilihan lama dipertahankan |
| `train_svm_optuna` / `train_naive_bayes_optuna` | Optuna TPE |
| `train_transformer` | Fine-tuning IndoBERT, seleksi validation |

## Menjalankan Optuna

Jalankan cell paling bawah yang berjudul **TUNING OPTUNA**. Cell tersebut
menemukan root proyek dan mengatur dataset serta 10 chat uji sendiri.

- `OPTUNA_TRIALS = 50`: trial per model, bukan epoch dan bukan semua kombinasi.
- `OPTUNA_CV_FOLDS = 5`: fold cross-validation.
- `OPTUNA_TIMEOUT = None`: tanpa batas waktu; isi detik untuk membatasi pencarian.
  Trial yang sudah berjalan tetap diselesaikan.
- `OPTUNA_N_JOBS = -1`: semua CPU untuk fold CV. Gunakan 1 untuk eksekusi serial.

Optuna sudah tercantum dalam requirements.txt. Jika belum terpasang pada kernel,
jalankan `%pip install optuna`, lalu restart kernel.

SVM Optuna mencari C secara logaritmik pada 0.25–8; NB mencari alpha pada
0.01–2. Pilihan fitur mencakup rentang Grid Search, tetapi Optuna tidak menjamin
mencoba setiap nilai Grid Search. Trial berjalan berurutan dengan seed 42.

## Kalibrasi SVM dan interpretasi

SVM Optuna menggunakan kalibrator yang membungkus seluruh pipeline TF-IDF + SVM.
Struktur ini dipakai dalam CV maupun refit, sehingga vocabulary/IDF tidak fit
pada fold kalibrasi. CV luar memiliki kalibrasi internal, jadi prosesnya lebih
berat daripada NB. Implementasi baseline/Grid Search lama tetap dipertahankan;
perbandingan SVM Optuna dengan Grid Search mencakup perbedaan alur kalibrasi,
bukan hanya algoritma pencarian.

## File hasil

Model: `intent_classifier_nb_optuna.pkl` dan `intent_classifier_svm_optuna.pkl`.
Pemanggilan ulang mengganti model Optuna terkait, tetapi tidak mengganti model
baseline/Grid Search. Pilih filename eksplisit saat memanggil `predict_intent`.

Setiap run menyimpan direktori unik di `models/optuna_results/`:
- `trials.csv`: kandidat, skor CV, skor per fold, dan durasi trial; disimpan per trial.
- `summary.json`: konfigurasi terbaik, versi Optuna, seed, metrik, dan laporan data.
- `split_indices.json`: indeks train/test serta CV untuk audit pemisahan data.

Riwayat ini untuk pelaporan, belum merupakan fasilitas resume study.
Durasi notebook mencakup pencarian, refit, evaluasi, dan penyimpanan, bukan
latensi satu chat. Gunakan CV untuk memilih konfigurasi; test dan 10 chat uji
bukan masukan untuk objective.
