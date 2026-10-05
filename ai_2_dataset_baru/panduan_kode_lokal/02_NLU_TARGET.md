# NLU target: siapa yang dituduh atau dibela?

Modul ini melanjutkan [NLU intent](01_NLU_INTENT.md). Intent membaca maksud umum; target membaca orang dan hubungan yang disebut.

## 1. Bayangkan memberi panah pada kalimat

Andi berkata: “Budi mencurigakan, tapi Citra bukan Hitman.”

Makna yang kita harapkan:

```text
Andi ──menuduh──> Budi
Andi ──membela──> Citra
```

Satu chat dapat berhubungan dengan lebih dari satu orang dan memiliki relasi berbeda. Model target tidak boleh sekadar mengambil semua nama dan menempelkan label intent yang sama kepada semuanya.

**Contoh ini adalah makna yang diharapkan.** Audit model asli justru menemukan relasinya terbalik pada kalimat tersebut. Kita memakainya untuk memahami tugas model, bukan mengklaim model sudah berhasil.

## 2. File dan fungsi utama

- [nlu_target.ipynb](../nlu_target.ipynb): dataset pasangan, training, evaluasi target.
- [nlg.py](../../../../Games/backend/services/npc_brain/generated/nlg.py): cari `NLUIndoBERT.target`, `buat_teks_pasangan`, dan `samarkan_nama` untuk jalur runtime.
- Ketiga notebook NPC juga memuat definisi NLU untuk dijalankan mandiri; game memakai NLU bersama dari runtime.

| Cari dengan Ctrl+F | Kegunaan |
| --- | --- |
| `load_target_dataset` | Membaca kolom JSON dan memeriksa konsistensi pengirim/target. |
| `samarkan_nama` | Mengganti nama dengan penanda peran relatif terhadap kandidat. |
| `buat_teks_pasangan` | Menyusun teks satu pesan untuk satu kandidat. |
| `bentuk_pasangan` | Memperbanyak satu pesan menjadi beberapa contoh kandidat saat training. |
| `NLUIndoBERT.target` | Memeriksa seluruh pemain roster saat inferensi. |
| `terapkan_ambang` / `pilih_ambang` | Aturan cadangan minimal satu target dan pemilihan ambangnya. |
| `_evaluasi_pesan` | Mengukur apakah kumpulan target-relasi satu pesan benar. |

## 3. Model ini memilih kelas hubungan, bukan menghafal daftar nama

Misalnya roster berisi Nara, Andi, Budi, Citra. Untuk chat Andi, sistem membuat satu pertanyaan per kandidat:

| Kandidat yang diperiksa | Pertanyaan model | Label yang mungkin |
| --- | --- | --- |
| Nara | Apa hubungan chat ini dengan Nara? | offend / defend / tidak_ada |
| Andi | Apakah Andi sedang membela atau menyerang dirinya? | offend / defend / tidak_ada |
| Budi | Apa hubungan chat ini dengan Budi? | offend / defend / tidak_ada |
| Citra | Apa hubungan chat ini dengan Citra? | offend / defend / tidak_ada |

Nama pemain dikembalikan oleh program yang menyusun pasangan. Keluaran kelas model adalah **relasi**. Karena kandidat berasal dari roster, sistem dapat bekerja dengan nama yang berbeda dari nama training.

Jika ada enam pemain dan intent tidak netral, ada enam input pasangan yang dapat diproses sebagai satu batch. Pengirim tetap diperiksa karena kalimat “aku bukan Hitman” bisa membela diri sendiri.

## 4. Mengapa nama diganti dengan penanda?

Bayangkan guru menunjuk satu murid dan bertanya: **“Kalimat ini sedang menuduh murid yang saya tunjuk, membelanya, atau tidak membahasnya?”** Murid yang ditunjuk itulah kandidat. Setelah selesai, guru menunjuk murid lain dan mengulang pertanyaan yang sama.

Model target bekerja seperti itu. Untuk satu chat, program membuat satu input untuk setiap kandidat. Nama disamarkan agar model dapat mempelajari hubungan dalam kalimat tanpa harus bergantung pada nama Budi, Andi, atau Citra.

| Penanda teks | Makna |
| --- | --- |
| `KANDIDAT_X` | Pemain yang sedang diperiksa dalam input ini. |
| `PENGIRIM_X` | Pengirim chat sekarang, jika ia bukan kandidat. |
| `PEMAIN_X` | Pemain lain yang bukan kandidat maupun pengirim. |
| `TIDAK_DIKETAHUI` | Target pada anotasi konteks sebelumnya belum diketahui. |

Tiga penanda pertama dipakai oleh `samarkan_nama` untuk mengganti nama di teks. `buat_teks_pasangan` juga menandai pengirim dan anotasi konteks melalui fungsi lokal `peran`; di sinilah `TIDAK_DIKETAHUI` digunakan. Jadi penanda terakhir bukan pengganti otomatis untuk setiap kata atau nama yang tidak dikenali.

### Satu contoh, diperiksa tiga kali

Roster: Andi, Budi, Citra. **Andi berkata: “Aku curiga Budi.”**

| Kandidat | Potongan input yang dibaca model | Relasi yang diharapkan |
| --- | --- | --- |
| Budi | `pesan sekarang PENGIRIM_X: Aku curiga KANDIDAT_X` | `offend`: kandidat sedang dituduh. |
| Citra | `pesan sekarang PENGIRIM_X: Aku curiga PEMAIN_X` | `tidak_ada`: yang dituduh adalah pemain lain. |
| Andi | `pesan sekarang KANDIDAT_X: Aku curiga PEMAIN_X` | `tidak_ada`: kandidat yang berbicara, tetapi ia menuduh orang lain. |

Ini potongan input dan label yang diharapkan, bukan hasil inferensi yang dijamin. Input lengkap juga memiliki intent dan konteks seperti bagian 5.

Pada baris Budi, model membaca “Aku curiga orang yang sedang diperiksa”. Pada baris Citra, model membaca “Aku curiga orang lain”. Pada baris Andi, letak `KANDIDAT_X` sebelum titik dua menunjukkan bahwa orang yang diperiksa adalah pembicara. **Menjadi kandidat tidak berarti menjadi tersangka; semua pemain mendapat giliran diperiksa.**

Kata “Aku” tetap ada di dalam kalimat pada contoh ini. Yang diganti di badan pesan adalah nama Budi; penanda sebelum titik dua berasal dari identitas pengirim. Jika pengirim sekaligus kandidat, penanda kandidat didahulukan.

### Kalau nama dihapus, bagaimana model mengembalikan Budi?

Program masih menyimpan pasangan antara input dan nama kandidat. Misalnya:

```text
Input untuk Budi  → model memilih offend    → program mencatat Budi: offend
Input untuk Citra → model memilih tidak_ada → tidak dimasukkan ke daftar target
Input untuk Andi  → model memilih tidak_ada → tidak dimasukkan ke daftar target
```

Nama asli tetap ada dalam data game. Penyamaran hanya terjadi pada teks yang disiapkan untuk model; username dan identitas pemain di engine tidak berubah.

### Mengapa ini membantu, dan apa batasnya?

“Aku curiga Budi” saat kandidat Budi dan “Aku curiga Raka” saat kandidat Raka sama-sama menjadi “Aku curiga `KANDIDAT_X`”. Model bisa mempelajari pola tuduhannya untuk nama yang berbeda. Akan tetapi, penyamaran saja tidak menjamin prediksi benar: model tetap harus memahami negasi, konteks, dan hubungan antarkalimat.

`PEMAIN_X` juga menyederhanakan identitas: beberapa pemain lain bisa memiliki penanda yang sama dalam satu input. Itu kompromi representasi; jangan menganggap setiap identitas orang lain masih dibedakan sepenuhnya di teks tersamarkan.

Istilah “token” di nama konstanta berarti **penanda teks buatan program**. Jangan langsung menganggap satu penanda pasti menjadi satu token khusus di tokenizer BERT; tokenizer masih memecah input sesuai kosakatanya. Konstanta `TOKEN_TIDAK_DIKETAHUI` berisi `"TIDAK_DIKETAHUI"`, tanpa akhiran `_X`. Format training dan inferensi harus konsisten.

Saat membaca kode, ikuti `buat_teks_pasangan` → `samarkan_nama` → `token_for`. `_nama_cocok` membantu mengenali potongan nama dan beberapa akhiran. Kata ganti, istilah game, dan kata umum membatasi pencocokan perkiraan; tetapi pencocokan username persis diperiksa lebih dahulu. Karena itu username seperti “aku” masih dapat berbenturan dengan kata biasa, seperti ditemukan dalam audit.

## 5. Mengapa perlu riwayat chat?

Andi: “Aku curiga Budi.”
Citra: “Iya, aku juga curiga dia.”

Chat Citra tidak menyebut Budi. Model harus membaca konteks untuk memperkirakan siapa “dia”. `anotasi_chat` membawa sampai **12 chat sebelumnya** bersama anotasi intent-targetnya.

`buat_teks_pasangan` menyusun:

```text
intent <label>
|| pesan sekarang <pengirim>: <teks tersamarkan>
|| konteks: <pesan terbaru> | <pesan lebih lama> | ...
```

Riwayat dimasukkan dari terbaru ke terlama. Maksimum token target default 512; menempatkan pesan utama dan konteks baru di depan membantu saat input terpotong. Tidak berarti 12 pesan selalu muat utuh.

Anotasi konteks saat game berjalan berasal dari prediksi sebelumnya. Jika prediksi lama salah, kesalahannya bisa memengaruhi pembacaan referensi berikutnya. Evaluasi memakai label konteks dari dataset tidak otomatis mengukur dampak rantai kesalahan ini.

## 6. Cara memilih hasil target

Baca `NLUIndoBERT.target`:

1. Jika intent `neutral`, langsung kembalikan daftar kosong.
2. Bentuk input pasangan untuk setiap pemain.
3. Tokenisasi, jalankan model, lalu softmax untuk probabilitas relasi.
4. Untuk tiap kandidat, pilih kelas dengan probabilitas paling tinggi.
5. Ambil kandidat yang kelasnya bukan `tidak_ada`.
6. Jika semua kandidat tidak_ada, periksa aturan minimal satu target.
7. Jika tetap tidak ditemukan, kembalikan target `tidak_diketahui`.

Contoh format hasil:

```python
[
    {"pemain": "Budi", "relasi": "offend", "prob": 0.91},
    {"pemain": "Citra", "relasi": "defend", "prob": 0.88},
]
# Ilustrasi struktur data; angkanya bukan hasil inferensi contoh di atas.
```

**`tidak_ada` berbeda dengan `tidak_diketahui`.** Yang pertama adalah kelas per kandidat: orang ini tidak terkait. Yang kedua adalah hasil tingkat pesan: sistem belum berhasil menentukan siapa targetnya.

Ambang pada `ambang_target.json` bukan penyaring semua hasil secara umum. Ia dipakai saat **tidak ada satu pun** target terpilih: ambil kandidat dengan probabilitas relasi sesuai intent tertinggi bila melewati ambang. Kandidat yang sudah terpilih lewat argmax tidak terlebih dahulu harus melewati ambang cadangan ini. Ini juga bukan mekanisme yang selalu memaksa ada target.

## 7. Training dan pembagian data

Satu pesan di dataset memuat pengirim, teks, intent, daftar pemain, target-relasi, konteks, jenis kasus, dan `source_group`.

Pesan dibagi dahulu dengan `StratifiedGroupKFold`, berdasarkan grup sumber dan distribusi kasus. Baru sesudah itu `bentuk_pasangan` membuat contoh per kandidat. Tujuannya agar pasangan yang berasal dari sumber sama tidak tersebar ke train dan test.

Notebook juga dapat menambah kandidat nama semu untuk melengkapi roster. Mereka menjadi contoh negatif `tidak_ada` karena tidak menjadi target pada pesan itu.

IndoBERT target memakai konfigurasi panjang 512, batch training 4, gradient accumulation 4, dan maksimum 12 epoch dalam konfigurasi saat ini. Train/validation/test berbasis grup memakai jumlah fold yang dibulatkan; ukuran akhirnya tidak selalu tepat 65/15/20. Ambang IndoBERT dipilih memakai validation; model klasik memakai prediksi out-of-fold train. Test dipakai untuk penilaian akhir.

## 8. Kenapa accuracy saja tidak cukup?

Jika ada enam pemain tetapi satu target, lima kandidat mungkin `tidak_ada`. Menebak terlalu sering tidak_ada dapat terlihat bagus pada accuracy, padahal target penting terlewat.

Periksa:

- `f1_macro_relasi`: kualitas offend dan defend.
- `target_precision`: apakah target-relasi yang dipilih tepat?
- `target_recall`: apakah target-relasi yang seharusnya ada berhasil ditemukan?
- `exact_match`: apakah seluruh kumpulan pasangan untuk satu pesan cocok persis?
- `per_case`: kelemahan khusus negasi, referensi, beberapa target, perubahan sikap, dan sebagainya.

Contoh: seharusnya offend Budi + defend Citra. Hanya menemukan offend Budi berarti sebagian benar, tetapi exact match tetap salah.

## 9. Ke mana hasilnya pergi?

Hasil masuk ke `Ingatan.chat[*].target`. `relasi_chat` memilih relasi yang valid untuk roster dan cukup jelas menurut confidence intent. Kemudian `hitung_bukti` memakai relasi itu untuk menghitung tekanan, dukungan, pengalihan, dan bukti lain.

Karena itu, **salah target bisa merusak keputusan ketiga metode sekaligus**. Mengubah bobot utility tidak menyelesaikan masalah jika kalimat pembelaan sudah dibaca sebagai tuduhan.

Saat menelusuri error, periksa input pasangan persis yang dibaca model, kelas di `config.id2label`, prediksi per kandidat, dan konteks 12 pesan. Jangan hanya melihat daftar target akhir.
