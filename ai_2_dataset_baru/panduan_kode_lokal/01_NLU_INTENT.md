# NLU intent: memahami maksud sebuah chat

Baca [peta sistem](00_MULAI_DI_SINI.md) jika belum tahu letak modul ini.

## 1. Contoh paling sederhana

Bayangkan guru meminta kita memberi stiker pada kalimat:

| Chat contoh | Makna yang diharapkan | Label |
| --- | --- | --- |
| “Aku curiga Budi itu Hitman.” | Menuduh/menyerang | `offend` |
| “Aku bukan Hitman, jangan asal tuduh.” | Membela | `defend` |
| “Ada yang punya info?” | Bertanya tanpa menetapkan tuduhan/pembelaan | `neutral` |

Ini **contoh makna**, bukan aturan pencarian kata yang menjamin hasil. Model belajar dari contoh data. Ia bisa salah membaca negasi, sindiran, atau gabungan dua maksud.

Intent menjawab **“kalimat ini sedang melakukan apa?”**. Ia belum menjawab siapa targetnya, apakah tuduhannya benar, atau role asli pengirimnya.

## 2. File yang perlu dibuka

- [nlu_baru.ipynb](../nlu_baru.ipynb): persiapan data, training, pembanding model, dan evaluasi intent.
- [nlg.py hasil ekspor](../../../../Games/backend/services/npc_brain/generated/nlg.py): cari `NLUIndoBERT.intent` untuk inferensi yang dipakai runtime bersama.
- [runtime.py](../../../../Games/backend/services/npc_brain/runtime.py): cari `_buat_nlu` dan `NLUBersama`.

Nama `nlg.py` bisa membingungkan: di dalamnya juga ada kelas NLU, karena penulis kalimat perlu membaca ulang hasil tulisannya. Runtime membuat satu NLU bersama dari kelas tersebut untuk anotasi chat dan validasi NLG.

## 3. Belajar dahulu, memprediksi kemudian

**Training** seperti belajar dari soal beserta kunci jawaban. Bobot model diubah agar jawabannya makin sesuai label.

**Inferensi** seperti mengerjakan soal baru memakai pengetahuan yang sudah tersimpan. Saat game berjalan, chat tidak otomatis melatih ulang model.

Alur notebook:

1. `load_clean_nlu_dataset` membaca kolom `teks_chat` dan `label_intent`.
2. Baris kosong dibuang; spasi dirapikan dan label diseragamkan.
3. Pasangan teks-label yang sama dibuang duplikatnya. Jika teks identik mempunyai label bertentangan, semua baris teks itu dibuang.
4. Data dibagi menjadi latihan, validation, dan test.
5. Model dilatih; validation dipakai memilih konfigurasi/checkpoint.
6. Model terpilih dievaluasi pada test dan disimpan.

IndoBERT memakai pembagian default 65% train, 15% validation, 20% test. Cari `_split_transformer_dataset`: test disisihkan lebih dahulu, lalu validation diambil dari sisa train. SVM/NB memakai test 20% yang sama, dengan tuning/CV pada bagian train. Pembersihan duplikat persis tidak berarti semua parafrasa yang sangat mirip ikut dikelompokkan.

## 4. Kenapa ada SVM, Naive Bayes, dan IndoBERT?

Notebook membandingkan beberapa pendekatan:

| Model | Gambaran mudah | Fitur |
| --- | --- | --- |
| Naive Bayes | Menggabungkan kecenderungan kata/pola terhadap label. | TF-IDF. |
| SVM | Belajar batas yang memisahkan kelompok kalimat. | TF-IDF; kalibrasi dipakai untuk probabilitas. |
| IndoBERT | Membaca hubungan token dalam kalimat, lalu memilih kelas. | Tokenizer dan jaringan Transformer yang di-fine-tune. |

`Grid Search` mencoba kombinasi parameter yang disediakan. `Optuna` memilih percobaan berikutnya berdasarkan hasil percobaan sebelumnya. Keduanya dipakai dalam eksperimen notebook; bukan dijalankan setiap pemain mengirim chat.

Jalur NPC notebook dalam game mencoba memakai IndoBERT intent **dan** IndoBERT target. Jika tidak tersedia/gagal dimuat, `NLUCadangan` memakai pemetaan label SVM lama dan pencarian nama sederhana. Status `sumber` pada `NLUBersama` membedakan jalur utama dan cadangan. Hasil eksperimen cadangan tidak boleh dianggap identik dengan IndoBERT.

## 5. Apa yang dilakukan IndoBERT saat menerima pesan?

Cari `NLUIndoBERT.intent`, lalu baca dengan urutan ini:

1. **Normalisasi nama:** `varian_nama_intent` mengganti nama pemain yang dikenali dengan tiga variasi nama kanonik.
2. **Tokenisasi:** teks diubah menjadi ID token yang dapat dibaca jaringan. Token bukan selalu satu kata utuh.
3. **Pembatasan panjang:** batas default intent 128 token; panjang disesuaikan dari `config.nlu_max_length` jika ada.
4. **Forward pass:** model menghasilkan skor kelas, disebut logits.
5. **Softmax:** skor diubah menjadi nilai probabilitas kelas yang jumlahnya 1.
6. **Rata-rata variasi:** probabilitas ketiga variasi nama dirata-ratakan, jika variasi dibuat.
7. **Argmax:** pilih indeks dengan nilai tertinggi; `config.id2label` menerjemahkannya menjadi nama label.
8. Kembalikan pasangan `(label, confidence)`.

Contoh bentuk hasil:

```python
("offend", 0.92)  # contoh format, bukan hasil uji kalimat tertentu
```

Angka 0,92 adalah keyakinan model terhadap label kalimat. **Bukan** peluang 92% bahwa target benar-benar Hitman. Confidence tinggi pun bisa salah.

Mengganti nama membantu model yang dilatih dengan nama manusia menghadapi username seperti `andy123`. Tapi ada celah saat username sama dengan kata seperti `aku` atau `hitman`; lihat bagian batasan.

## 6. Hasilnya dipakai di mana?

`anotasi_chat` menyimpan hasil menjadi field `intent` dan `conf_intent`, kemudian memanggil NLU target. Hasil lengkap masuk ke `Ingatan.chat`.

Lalu `relasi_chat` pada modul NPC memeriksa:

```text
intent offend/defend DAN confidence >= 0,60?
  ya    → relasi target yang valid boleh menjadi bukti
  tidak → jangan memakai relasi itu sebagai bukti tuduhan/pembelaan
```

`neutral` tetap berguna. Kalimat netral dapat menjadi pertanyaan langsung, tanda aktivitas, atau petunjuk bahwa ruangan sedang berdiskusi. “Tidak menjadi bukti menuduh” tidak sama dengan “dibuang seluruhnya”.

`NLUBersama` menyimpan hasil yang pernah dihitung dalam memo/cache. Kuncinya mencakup teks dan roster agar normalisasi nama tidak tertukar. Lock menyerialkan inferensi; salinan hasil dikembalikan agar memori antarbot tidak berbagi objek yang bisa berubah.

## 7. Parameter yang paling membantu saat membaca kode

| Parameter/fungsi | Artinya | Kapan diperhatikan? |
| --- | --- | --- |
| `TRANSFORMER_EPOCHS = 12` | Batas maksimum putaran belajar; early stopping bisa berhenti lebih awal. | Training. |
| `learning_rates` | Pilihan besar langkah pembaruan bobot. | Memilih konfigurasi lewat validation. |
| `max_length = 128` | Panjang input token intent. | Kalimat panjang berisiko terpotong. |
| `gradient_accumulation_steps` | Mengumpulkan gradien beberapa batch kecil sebelum memperbarui bobot. | Menyesuaikan kebutuhan memori training. |
| `MIN_CONF_INTENT = 0.60` | Ambang pemakaian bukti di otak NPC. | Game menilai apakah hasil intent cukup jelas. |
| `local_files_only=True` | Memuat model dari berkas lokal. | Startup tidak otomatis mengunduh model. |

## 8. Membaca hasil evaluasi

- **Accuracy:** bagian prediksi yang benar.
- **Precision per kelas:** saat model mengatakan offend, berapa banyak yang memang offend?
- **Recall per kelas:** dari semua offend asli, berapa yang berhasil ditemukan?
- **F1 macro:** rata-rata F1 tiap kelas, sehingga kelas kecil tidak tenggelam dalam kelas besar.
- **Confusion matrix:** tabel yang menunjukkan kelas mana sering tertukar dengan kelas mana.

Metrik test mengukur sampel test yang dipakai. Ia bukan jaminan semua slang, negasi, atau username baru akan terbaca benar.

## 9. Batasan yang sudah terlihat di proyek ini

Audit model asli menemukan “Menurutku Budi bukan Hitman.” terbaca offend dengan confidence sekitar 0,394. Filter 0,60 menahan relasi ini agar tidak menjadi bukti. Namun pada contoh kalimat campuran, intent sangat yakin sementara relasi target tetap salah. Karena itu NLU intent dan target perlu diuji sebagai satu rangkaian juga.

Saat melihat bot salah merespons, telusuri `teks → intent/conf_intent → target → relasi_chat` sebelum mengubah rumus fuzzy atau utility. Bisa saja metode penalarannya menerima input yang sudah salah.
