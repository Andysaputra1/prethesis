# Fine-tuning IndoBERT pada seluruh versi dataset

Konfigurasi berlaku untuk `v1`, `v2_100`, `v2_200`, `v3_300`, dan `v3_600` melalui
`modules/nlu_training.py`. Model tetap `indobenchmark/indobert-base-p1`.
Seluruh bobot backbone dan classifier dilatih; ini full fine-tuning, bukan hanya
mengambil embedding. Model dimuat dari cache lokal.

Status eksekusi 8 September 2026: pengguna meminta menghentikan training dan akan
menjalankan eksperimen sendiri. v3_600 sempat selesai (LR 3e-5, checkpoint sekitar
epoch 5, test macro-F1 0,7967, cocok 9/10 chat contoh). v3_300 dihentikan sebelum
seluruh trial selesai; versi lain belum dilatih ulang. Model v3_600 pada folder
model sudah diperbarui. Konfigurasi kode tersedia pada kelima notebook. Grafik dan
tabel hasil yang sudah diekspor saat ini hanya mencakup v3_600.

## Apakah empat epoch terlalu sedikit?

Tidak bisa ditentukan hanya dari jumlahnya. Satu epoch adalah satu lintasan atas
data training. IndoBERT sudah melewati pretraining; fine-tuning menyesuaikan bobot
tersebut pada tugas intent. Jumlah pembaruan juga bergantung pada jumlah sampel,
batch size, dan gradient accumulation.

Output lama notebook `v3_600` mencatat:

| Epoch | Training loss | Loss evaluasi | Macro-F1 evaluasi |
|---|---:|---:|---:|
| 1 | 1,0939 | 0,5730 | 0,7800 |
| 2 | 0,4764 | 0,4884 | 0,822257 |
| 3 | 0,3045 | 0,4951 | 0,815108 |
| 4 | 0,1859 | 0,5255 | 0,822243 |

Checkpoint terbaik ada pada epoch 2. Training loss terus turun sesudahnya,
sedangkan loss evaluasi naik. Ini mengindikasikan overfitting, sehingga menambah
epoch tanpa memantau generalisasi belum punya dasar.

Kode lama menggunakan **test set sebagai eval_dataset** untuk memilih checkpoint.
Karena itu angka tersebut bukan evaluasi test yang independen dari seleksi model.

## Protokol baru

Test 20% tetap sama dengan SVM/NB. Dari pool 80% sisanya, sekitar 15% seluruh data
diambil sebagai validation. IndoBERT dilatih pada sekitar 65% data.

| Versi | Train | Validation | Test |
|---|---:|---:|---:|
| v1 | 526 | 122 | 162 |
| v2_100 | 518 | 120 | 160 |
| v2_200 | 1049 | 243 | 323 |
| v3_300 | 1807 | 417 | 557 |
| v3_600 | 3636 | 840 | 1120 |

Setiap trial dimulai dari pretrained dan seed 42 yang sama. Checkpoint dan learning
rate dipilih dengan validation macro-F1. Test diprediksi sekali setelah pemenang
terkunci. SVM/NB memakai pool train 80% untuk training/CV; alokasi data internalnya
berbeda, meskipun test identik.

Test ini pernah dilihat dalam eksperimen lama. Protokol baru menghilangkan pemakaian
test dalam seleksi pada run ini, tetapi tidak mengubah riwayat tersebut. Untuk
klaim akhir skripsi, data chat baru yang dikurasi terpisah akan memberi pemeriksaan
generalisasi yang lebih kuat. Perbedaan skor lama dan baru bukan ablation epoch
yang terkontrol karena split internal dan konfigurasi training ikut berubah.

## Parameter yang tersedia

| Parameter notebook | Nilai awal | Fungsi |
|---|---|---|
| `TRANSFORMER_EPOCHS` | 12 | Batas maksimum, bukan target wajib |
| `learning_rates` | 1e-5, 2e-5, 3e-5 | Tiga trial independen; pilih dengan validation |
| `batch_size` | 8 | Sampel per forward/backward pada satu GPU |
| `gradient_accumulation_steps` | 2 | Effective batch 16 pada satu GPU |
| `eval_batch_size` | 16 | Batch saat evaluasi |
| `max_length` | 128 | Batas token termasuk token khusus; sama saat inference |
| `weight_decay` | 0,01 | Regularisasi bobot |
| `warmup_ratio` | 0,1 | Proporsi langkah awal untuk menaikkan learning rate |
| `lr_scheduler_type` | linear | Learning rate turun sesudah warmup; cosine juga tersedia |
| `dropout` | 0,1 | Dropout hidden state, attention, dan classifier |
| `label_smoothing_factor` | 0 | Bisa diuji untuk mengurangi target terlalu tajam |
| `max_grad_norm` | 1 | Gradient clipping |
| `early_stopping_patience` | 3 | Berhenti setelah 3 evaluasi tanpa perbaikan memadai |
| `early_stopping_threshold` | 0,001 | Ambang perbaikan validation macro-F1 untuk patience |
| `gradient_checkpointing` | False | Opsi menghemat memori dengan komputasi tambahan |

Semua parameter di atas dapat diubah; **pencarian otomatis saat ini hanya untuk
learning rate dan pemilihan checkpoint/epoch**. Parameter lainnya adalah konfigurasi
awal, belum terbukti optimal. Ambang early stopping memengaruhi kapan berhenti;
checkpoint yang disimpan tetap berdasarkan skor validation tertinggi yang tercatat.
Batch 8 dengan accumulation 2 mengurangi kebutuhan memori, tetapi tidak menjamin
hasil numerik identik dengan batch langsung 16.

Audit tokenizer pada **split train saja** mencatat maksimum 23 token untuk v1,
v2_100, dan v2_200; 32 untuk v3_300; dan 33 untuk v3_600, termasuk token khusus.
Tidak ada chat train yang terpotong pada batas 128. Menaikkan batas itu belum
menambah informasi pada data train yang tersedia. Padding dilakukan dinamis per
batch. Detail ada di `indobert_token_lengths.json`.

## Menjalankan dan membaca hasil

Restart kernel notebook bila modul lama sudah terimpor, lalu jalankan cell path dan
setup. Untuk IndoBERT saja:

```python
hasil_transformer = train_transformer_model()
```

Untuk satu learning rate dan batas epoch berbeda:

```python
hasil_transformer = train_transformer_model(
    epochs=20,
    learning_rates=None,
    learning_rate=2e-5,
)
```

Untuk seluruh model, jalankan cell `run_all_nlu_models`. `RUN_TUNING` mengontrol
grid search SVM/NB; IndoBERT memakai `TRANSFORMER_OPTIONS`.

Dari root proyek, konfigurasi awal IndoBERT pada seluruh versi dapat dijalankan:

```powershell
venv/Scripts/python.exe -u scripts/tune_indobert.py
```

Tambahkan `--versions ai_1_nlu_v3_600` untuk satu versi. Script CLI memakai nilai
awal fungsi, sedangkan perubahan `TRANSFORMER_OPTIONS` berlaku untuk notebook.

Setiap folder `models/intent_classifier_transformer` berisi model dan tokenizer,
`metrics.json` (termasuk confusion matrix), `training_summary.json` (konfigurasi,
seleksi, serta history seluruh trial), dan `test_predictions.csv` untuk analisis
kesalahan. Folder `transformer_results/run_*` menyimpan indeks split, history,
serta checkpoint terbaik tiap trial. Checkpoint hanya menyimpan model, sehingga
tidak dipakai untuk resume optimizer. Script CLI menulis ringkasan lintas versi ke
`reports/indobert_tuning_results.json`.

Jalankan `venv/Scripts/python.exe scripts/plot_indobert.py` untuk mengekspor kurva
trial terpilih ke PNG/PDF dan tabel hasil ke CSV. Kurva memisahkan loss train,
loss validation, dan validation macro-F1; garis vertikal menandai epoch terpilih.

## Batas label yang perlu diperhatikan

Generator mendefinisikan `bluffing` sebagai berbohong tentang role, tetapi
`claiming` sebagai deklarasi role yang bisa jujur atau bohong. Kedua definisi
tumpang tindih untuk klasifikasi satu label. Contoh dataset:

- `bluffing`: "gw Spy, tadi malam aku Guard C karena pola geraknya paling rawan"
- `claiming`: "aku Spy, tadi malam aku pasang Guard ke Raka"

Satu chat publik tidak selalu cukup untuk memastikan kebohongan. Tinjau pedoman
anotasi dan, jika diperlukan, konteks percakapan publik untuk pengembangan dataset
berikutnya. Role rahasia tidak boleh dijadikan fitur bila tidak tersedia saat
inference. Tuning hyperparameter sendiri tidak menghilangkan ambiguitas label ini.

## Referensi implementasi

- [Tutorial fine-tuning IndoBERT dari IndoBenchmark](https://indobenchmark.github.io/tutorials/pytorch/deep%20learning/nlp/2020/10/18/basic-pytorch-en.html).
- [EarlyStoppingCallback, Transformers 4.46.3](https://huggingface.co/docs/transformers/v4.46.3/en/main_classes/callback#transformers.EarlyStoppingCallback).
- [TrainingArguments, Transformers 4.46.3](https://huggingface.co/docs/transformers/v4.46.3/en/main_classes/trainer#transformers.TrainingArguments).
