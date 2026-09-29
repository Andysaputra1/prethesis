# Dataset intent dan target berkonteks

Script: label_target.py. Status saat disiapkan: belum dijalankan untuk menghasilkan dataset dan belum menghubungi API.

## Apa yang dibuat

Sumber lama berisi teks_chat dan label_intent yang berdiri sendiri. Script tidak menganggap dua baris bertetangga sebagai satu percakapan.

Default per baris sumber:

1. Satu contoh original, teks dan intent sumber dipertahankan; chat_sebelumnya kosong.
2. Satu variasi sintetis tambahan untuk salah satu kasus yang dijadwalkan.

Teks utama variasi boleh berbeda agar kasus seperti kata ganti dan pergantian topik benar-benar bisa dilatih. Variasi tetap mengikuti intent utama sumber. Nama/pengirim yang tidak tersedia dalam CSV sumber ditetapkan sebagai tokoh simulasi, bukan diklaim sebagai metadata pemain asli.

Dengan N baris sumber dan satu variasi per sumber, rencana keluaran adalah 2N contoh. Jika memakai --case, hanya label sumber yang cocok dengan kasus itu yang dipilih.

## Lima kolom utama

| Kolom | Isi |
| --- | --- |
| pengirim | Nama/ID pembicara pada pesan sekarang. |
| teks_chat | Pesan sekarang yang akan diprediksi. |
| label_intent | Intent utama pesan sekarang: offend, defend, atau neutral. |
| chat_sebelumnya | JSON array maksimal 12 pesan berurutan. Setiap pesan memiliki pengirim, teks_chat, label_intent, dan target. |
| target | JSON array pasangan pemain dan relasi offend/defend untuk pesan sekarang. |

Neutral mempunyai target=[].
Pembelaan/tuduhan diri sendiri menggunakan nama/ID pengirim karena identitas pengirim tersedia dalam skenario.
Target yang tidak dapat ditentukan memakai pemain=tidak_diketahui, dengan relasi yang sesuai.
Pesan campuran dapat memiliki beberapa target dengan relasi berbeda.

Anotasi intent-target pada konteks adalah memori acuan yang ingin kita pelajari. Label jawaban pesan SEKARANG tidak masuk ke konteks. Di game, anotasi memori ini digantikan prediksi model; kualitas saat memakai memori prediksi tetap perlu diuji, tidak boleh hanya diuji dengan memori yang selalu benar.

## Kasus yang dibuat

| Kasus | Variasi |
| --- | --- |
| original | Teks sumber utuh tanpa konteks yang dikarang. |
| explicit | Target langsung pada pesan sekarang, termasuk "Aku yakin bukan Andy". |
| reference_start | Nama/acuan eksplisit di awal 12 konteks. |
| reference_middle | Nama/acuan eksplisit di posisi ke-6/7. |
| reference_end | Nama/acuan eksplisit di akhir konteks. |
| memory_outside_window | Nama eksplisit sudah keluar dari 12 konteks, tetapi memori di dalam jendela masih menentukan target secara jelas. |
| outside_window_unknown | Nama dan petunjuk memori yang menentukan target sudah tidak tersedia; hasil tidak_diketahui. |
| interruption | Diskusi disela obrolan lain, tetapi hubungan kembali ke target masih jelas. |
| topic_switch | Topik berpindah pemain; jangan mengikuti target lama secara otomatis. |
| ambiguous | Beberapa acuan sama-sama mungkin; jangan memaksa satu nama. |
| self | Membela atau menuduh/vote diri sendiri. |
| witness | Nama saksi/korban bukan otomatis target. |
| multiple_targets | Beberapa pemain mendapat relasi yang sama. |
| mixed_relations | Membela Budi sekaligus menuduh Andy, dengan kedua relasi tersimpan. |
| quotation | Bedakan ucapan yang dikutip dengan sikap pengirim. |
| negation | "Andy Hitman" berbeda dari "Andy bukan Hitman". |
| second_person | Kamu/lu hanya dipetakan jika dialog mendukung; tanpa acuan jelas gunakan tidak_diketahui. |
| first_message | Pembuka permainan, tanpa chat sebelumnya; boleh neutral atau target yang jelas pada teks sekarang. |
| first_message_unknown | Pesan pembuka memakai dia/kamu tanpa acuan; target tidak_diketahui. |
| first_message_self | Pesan pembuka membela/menuduh diri sendiri; target adalah pengirim. |
| short_history_1 | Tepat satu pesan sebelumnya. |
| short_history_2 | Tepat dua pesan sebelumnya. |
| short_history_3 | Tepat tiga pesan sebelumnya; acuan bisa berada pada pesan pertama. |
| neutral_names | Nama disebut tanpa tuduhan/pembelaan. |
| neutral_after_accusation | Konteks menuduh tetapi pesan sekarang neutral. |
| neutral_status | Klaim status/role atau pertanyaan informasi tanpa serangan/pembelaan. |

Kasus rotate per label sumber. Semua kasus tidak berarti setiap satu baris sumber digandakan menjadi semua kasus.
--variants-per-source mengatur jumlah variasi tambahan; --case memilih satu tipe variasi tertentu.
Karena konteks disimpan lengkap sebelum dipotong, jejak acuan yang lebih lama tetap dapat diperiksa pada checkpoint.

## Contoh memori

Contoh memori: pesan lama di luar jendela menyebut Andy. Pesan yang masih terlihat menyatakan "Bukan dia" dengan anotasi defend Andy, berdasarkan jejak lama. Pesan sekarang boleh menggunakan memori itu jika hubungan belum berubah. Script tidak menolak target hanya karena namanya tidak ada pada teks 12 pesan terakhir.

Contoh ambigu: jika jejak teks dan memori yang cukup tidak tersedia, target tetap tidak_diketahui. Pengetahuan pembuat skenario tidak boleh menjadi jawaban yang tidak dapat diperoleh model.

## Pemeriksaan otomatis

- Format respons diperiksa melalui schema.
- Roster/pengirim/target harus konsisten.
- Setiap target dikenal mempunyai nomor bukti teks atau memori sebelumnya.
- Bukti tidak boleh menunjuk masa depan atau melompati jendela tanpa rantai memori.
- Target yang tidak dikenal/ambigu tidak dipaksakan menjadi pemain.
- Original harus mempertahankan teks dan intent sumber.
- Kasus posisi acuan, memori luar jendela, self, dan multi-target mempunyai pemeriksaan struktur.
- Setiap pesan diverifikasi lewat panggilan model terpisah, hanya memakai konteks sebelumnya.
- Jika gagal, sesi dibuat ulang maksimal --attempts kali; setelah itu proses berhenti dan checkpoint sebelumnya tetap tersedia.

Pemeriksaan struktur dan model tidak menjamin semua makna/anotasi benar. Output sengaja bernama DRAFT. Verifier memakai model yang sama dengan generator sehingga masih bisa memiliki kesalahan yang sama. Jangan menyebut data ini gold terverifikasi manusia sebelum pemeriksaan manusia dilakukan.

Jika label sumber original memang tidak sesuai teks, verifier bisa menolak. Script tidak diam-diam mengganti label sumber agar lolos; perbaiki sumber secara terpisah setelah diperiksa.

## File keluaran saat nanti dijalankan

Untuk dataset_final3.csv:

- dataset_final3_context_target_draft.csv: enam kolom utama (pengirim, teks_chat, label_intent, chat_sebelumnya, daftar_pemain, target). daftar_pemain adalah roster sesi dalam JSON dan menjadi daftar kandidat model target.
- dataset_final3_context_target_draft.groups.jsonl: pemetaan baris output ke sesi, source_group, kasus, dan penanda sintetis.
- dataset_final3_context_target_draft.sessions/: percakapan lengkap, jejak bukti, checkpoint per sesi, dan konfigurasi run.

Tidak ada kolom needs_review atau file audit tabel seperti script lama.
groups.jsonl diperlukan agar semua turunan satu sumber masuk split yang sama. source_group menyatukan teks sumber identik setelah normalisasi spasi/huruf. Parafrasa atau keluarga template berbeda yang hampir sama masih perlu dideteksi dan dikelompokkan sebelum pembagian train/test.

Output dibuat sebagai file baru; sumber tidak ditimpa. Jangan menghapus file pendamping bila dataset akan dipakai untuk penelitian.

## Konfigurasi

| Opsi | Default / fungsi |
| --- | --- |
| --input | Wajib: pilih dataset yang akan dipakai. |
| --model | gpt-6-astra untuk generator dan verifier, sesuai permintaan model terbaru yang mengutamakan kualitas. |
| --reasoning-effort | medium untuk generator dan verifier, sesuai permintaan terbaru. |
| --batch-size | 50 contoh dalam satu permintaan generasi; batch terakhir boleh lebih sedikit. |
| --parallel-batches | 5 batch aktif bersamaan, hingga 250 contoh per gelombang. |
| --verify-workers | 4 sesi diverifikasi bersamaan, dengan konteks tiap pesan tetap kausal. |
| --reuse-checkpoints | Mengimpor hasil lulus yang tugas/sumbernya identik dari folder run lama. |
| --env-file | .env di root prethesis; membaca OPENAI_API_KEY tanpa menampilkan nilainya. |
| --limit | Jumlah baris sumber pertama. Tanpa opsi ini seluruh sumber. Baris pertama belum tentu mewakili semua intent. |
| --variants-per-source | 1, selain satu original per sumber. |
| --attempts | 4 percobaan; hanya contoh yang belum lolos yang diulang. |
| --case | Opsional memilih satu tipe variasi. |
| --resume | Melanjutkan checkpoint dengan sumber, model, pilihan, dan versi script yang sama. |
| --generate | Baru dengan opsi ini script mengirim data ke API dan membuat dataset. |
| --dry-run | Menampilkan rencana saja; sama seperti tanpa --generate. |

Jumlah 12 adalah batas pesan, bukan jaminan semua teks muat tokenizer. Saat training/inference, terapkan batas token yang sama dan prioritaskan pesan sekarang. Jika harus memangkas konteks, buang pesan paling lama dan uji lagi apakah jawaban masih dapat ditentukan dari informasi yang tersisa. Jangan mempertahankan label target pasti pada contoh yang seluruh bukti inputnya telah terpotong tanpa memori pendukung.

## Perintah untuk pengguna, belum dijalankan oleh asisten

Dari folder prethesis, tampilkan rencana dua baris sumber tanpa API:

~~~powershell
.\venv\Scripts\python.exe lama/generateDataset/label_target.py --input ai_2_nlu_v1_janice/data/dataset_final3.csv --limit 2
~~~

Nanti, setelah memeriksa desain dan memang ingin memanggil API, tambahkan --generate dan gunakan output percobaan baru:

~~~powershell
.\venv\Scripts\python.exe lama/generateDataset/label_target.py --input ai_2_nlu_v1_janice/data/dataset_final3.csv --limit 2 --output ai_2_nlu_v1_janice/data/percobaan_context_target.csv --generate
~~~

Untuk sumber di ai_2_dataset_baru, ganti path --input dan --output saja.
Perubahan dari pelabelan lama: ini membuat percakapan dan memverifikasi tiap pesannya, sehingga panggilan API bisa jauh lebih banyak. Satu permintaan generasi membuat hingga 50 contoh. Setelahnya, setiap pesan tetap memiliki satu panggilan verifikasi; hingga empat sesi diperiksa bersamaan. Retry generasi hanya memuat contoh yang gagal. Jangan langsung menjalankan seluruh dataset sebelum memeriksa percobaan kecil.

--resume memakai kembali checkpoint sesi yang sudah selesai, tetapi hanya jika konfigurasi sama dan output final belum ada.

## Pembaruan model, 25 September 2026

Default sekarang GPT-6 Astra dengan reasoning effort medium untuk generator dan verifier. Konfigurasi ini dicatat di checkpoint; resume menolak konfigurasi berbeda. Timeout per permintaan 1800 detik untuk memberi waktu pada respons batch yang panjang.

Dokumentasi resmi: https://developers.openai.com/api/docs/models/gpt-6-astra
Harga standar yang tercantum saat diperiksa adalah USD 10 per satu juta token input dan USD 50 per satu juta token output. Ini harga token, bukan estimasi biaya seluruh dataset. Biaya akhir bergantung pada panjang konteks, output/penalaran, verifikasi tiap pesan, dan retry. Akses akun ke model belum diuji melalui API.

## Pembaruan biaya, 26 September 2026

Verifikasi model sekarang mati secara default. Verifikasi memakai satu request per pesan dan menjadi sumber biaya terbesar: pada run 25 September, satu batch 50 contoh memakai 2 request generasi tetapi 166-241 request verifikasi. Tanpa `--verify`, hasil yang lolos pemeriksaan struktur lokal (`validate_session`) langsung disimpan dengan `model_verification_passed: false`. Tambahkan `--verify` untuk memakai verifikasi model lagi.

Total token dari respons API (input, output, dan reasoning) sekarang ditulis di setiap baris progress.txt.

## Kasus baru dan validasi, 26 September 2026

Empat kasus offend/defend ditambahkan (sekitar 135 contoh per kasus):

- agreement: menyetujui/membantah pesan lain tanpa menyebut ulang nama; target diwarisi dari anotasi pesan yang ditanggapi.
- plural_reference: mereka/kalian/keduanya untuk dua pemain atau lebih dari konteks.
- rhetorical_question: pertanyaan retoris yang menuduh atau membela, bukan pertanyaan informasi.
- stance_change: pengirim berubah sikap terhadap pemain yang sama; anotasi mengikuti sikap terbaru.

Definisi offend/defend/neutral kini ada di prompt generator (sebelumnya hanya di prompt verifier yang default-nya mati). Aturan tambahan di validate_session:

- Pesan sintetis dengan relasi offend harus berintent offend; teks original sumber dikecualikan.
- Satu pemain tidak boleh dituduh sekaligus dibela dalam satu pesan.
- Pesan sebelumnya dari pemain X menjadi bukti identitas untuk kamu/lu yang merujuk X.
- Penanda minimum per kasus: explicit, witness, negation, quotation, second_person, topic_switch, neutral_names, neutral_after_accusation, dan empat kasus baru. interruption, ambiguous (selain target tidak_diketahui), dan neutral_status tidak punya penanda teks yang andal.
- Kata ganti (aku, kamu, mereka, kalian, dan sejenisnya) ditolak sebagai nama peserta.

Pada 206 checkpoint GPT-6 Astra, 205 lolos aturan baru; satu topic_switch tanpa target lama di konteks ditolak. Checkpoint GPT-6 Astra dan semua folder trial Bedrock dihapus pada 26 September 2026 agar dataset dibuat ulang oleh satu model dengan aturan terbaru. Saat impor dengan --reuse-checkpoints, model lama boleh berbeda.

Contoh yang tetap gagal setelah semua percobaan kini dicatat di failed.jsonl dan tidak menghentikan batch lain. CSV hanya memuat contoh yang lolos; ulangi yang gagal dengan output baru dan --reuse-checkpoints ke folder sessions run sebelumnya.

Belum ditangani: sarkasme dan kalimat pengandaian.

## Nama panggilan, 26 September 2026

Kasus nickname (sekitar 364 contoh; offend, defend, dan neutral) memakai nama panggilan, singkatan, atau salah ketik ringan tanpa menulis nama asli, misalnya Andy -> ndy/andi. Generator mengeluarkan field panggilan: daftar {pemain, sebutan}. Di kasus lain panggilan boleh sesekali dipakai; jika tidak ada, panggilan=[].

Sebutan hanya diterima jika mirip nama aslinya (potongan nama, ejaan mirip dengan rasio >= 0,6, atau inisial), bukan kata ganti/kata umum, bukan nama peserta lain, dan tidak juga cocok untuk pemain lain. Semua pemeriksaan penyebutan nama (bukti identitas, posisi acuan, memori luar jendela, saksi, agreement, dan lainnya) menerima nama asli maupun sebutan yang tercatat.

Target, daftar_pemain, dan anotasi konteks tetap memakai nama asli. panggilan tidak masuk CSV karena game tidak mengetahuinya saat inferensi; field ini disimpan di checkpoint dan groups.jsonl untuk evaluasi. Checkpoint lama tanpa field panggilan tetap valid.

## Awal permainan dan bahasa percakapan

Kasus awal sekarang dipisah tegas: 0, 1, 2, atau 3 pesan sebelumnya. Panjang tiap kasus diperiksa persis; tidak boleh menambahkan pesan pengisi sampai 12. Pembuka permainan tidak mengarang hasil malam, voting, atau pembahasan yang belum terjadi. Chat berurutan boleh dikirim orang yang sama, tidak harus bergantian.

- Tanpa konteks: chat_sebelumnya=[]; nama eksplisit tetap bisa diketahui.
- Aku/gue/gw: target diri sendiri menggunakan identitas pengirim.
- Dia/kamu/lu tanpa acuan: tidak_diketahui, meskipun daftar peserta tersedia.
- Neutral: target=[] pada semua panjang konteks.
- Kasus 1, 2, dan 3 konteks dijadwalkan terpisah untuk offend, defend, dan neutral. Ketiganya bukan lagi pilihan bebas dari satu kasus short_history.

Instruksi generator meminta bahasa chat Indonesia natural: santai sesuai karakter dan panjang pesan bervariasi. Singkatan/typo ringan hanya pada slot terjadwal sekitar 1,5% pesan sintetis; sisanya memakai ejaan jelas. Dilarang mengisi riwayat dengan timer atau kalimat berulang semata-mata untuk mencapai jumlah pesan.

Verifier memeriksa intent dan target setiap pesan secara berurutan, termasuk seluruh konteks. Pesan yang salah/meragukan menghentikan verifikasi sesi dan memicu pembuatan ulang sesuai batas percobaan. Verifier juga memeriksa kewajaran bahasa/alur teks sintetis. Teks original tidak ditulis ulang demi gaya bahasa.

Pemeriksaan ini tetap otomatis, bukan jaminan bahwa anotasi pasti bebas kesalahan. Contoh JSON merupakan ilustrasi lokal; dataset hasil generator belum dibuat.

## Batas singkatan dan typo ringan

Sekitar 1,5% pesan sintetis yang tampil dalam CSV (pesan utama dan konteksnya) mendapat slot satu singkatan atau typo ringan: satu slot setiap 67 pesan. Panjang sesi ditentukan sebelum generasi agar kuota tidak bergantung pada kebebasan model memilih panjang. Nomor slot disimpan pada job/checkpoint dan file kelompok, bukan sebagai kolom tambahan dataset.

Di luar slot tersebut, bahasa tetap santai dengan ejaan jelas. Verifier memeriksa kepatuhan gaya setiap pesan. Penjadwalan kuota terukur; penilaian bahasa oleh AI masih memerlukan tinjauan hasil. Teks original dipertahankan apa adanya sehingga rasio typo pada seluruh dataset, termasuk sumber lama, tidak dijamin 1,5%.

## Batch 50 dan lokasi progres

Versi sekarang membuat 50 contoh dalam SATU request generasi, bukan lima request berisi sepuluh. Lima checkpoint lama yang lulus dapat diimpor melalui --reuse-checkpoints. Asal dan konfigurasi high pada hasil lama tetap tercatat; generasi baru memakai medium. Folder dan dataset lama tidak ditimpa.

Run baru memakai output dataset_final3_context_target_batch50_medium_20260925.csv. Folder pendampingnya dataset_final3_context_target_batch50_medium_20260925.sessions berisi:

- progress.txt: waktu pembaruan, jumlah hasil selesai, nomor batch, dan fase proses atau alasan berhenti.
- r..._v....json: satu hasil yang sudah lolos pemeriksaan.
- raw_batches/: respons batch sebelum pemeriksaan; ini belum berarti semua anotasinya lulus.
- run.json: konfigurasi proses.

Jumlah selesai tidak bertambah saat model masih menyusun batch. Setelah verifikasi, setiap contoh yang lulus segera disimpan. Jika proses berhenti, checkpoint lulus dapat dilanjutkan dengan --resume dan konfigurasi yang sama. Respons mentah disimpan untuk diperiksa; resume memakai checkpoint lulus, bukan otomatis mempercayai respons mentah.

## Lima batch paralel

Run aktif terbaru memakai dataset_final3_context_target_batch50_parallel5_medium_20260925.csv dan folder .sessions dengan nama yang sama. Lima request generasi dapat berjalan bersamaan, masing-masing berisi 50 contoh. Ketika satu batch selesai diverifikasi, slotnya dipakai batch berikutnya.

Batas verifikasi tetap empat sesi secara total, bukan empat per batch. Semua pesan dalam tiap sesi diperiksa berurutan dengan konteks masa lalu. Progress.txt menampilkan jumlah hasil selesai dan status tiap batch aktif; penulisannya dikunci agar tidak bertabrakan. Hasil lama tetap diimpor tanpa mengganti metadata effort aslinya.

## Akses model dan pelajaran trial Bedrock, 26 September 2026

Ping langsung ke Bedrock (us-east-1) dengan API key saat ini. Status katalog tidak bisa diandalkan: Sonnet 4.6 tertulis NOT_AVAILABLE tetapi bisa dipanggil.

- Bisa dipanggil: Claude Opus 4.6, Opus 4.5, Sonnet 4.6, Sonnet 4.5, Haiku 4.5; Kimi K3, Kimi K2.5, GLM-5, DeepSeek V3.2, Mistral Large 3, MiniMax M2.5, Qwen3 Next 80B, gpt-oss-120b.
- Ditolak "not available for this account": Claude Fable 5/5.1, Opus 5.5, Opus 5, Opus 4.8, Opus 4.7, Sonnet 5; semua GPT-6 dan GPT-5.x; Grok 4.6.

Trial 50 job yang sama (catatan ringkas; folder trial sudah dihapus):

- Haiku 4.5: 18/50 lolos; satu percakapan templat disalin ke banyak sesi (17 nama unik, "gw" di 199/307 pesan). Tidak layak.
- Sonnet 4.6: 22/50 lolos, jauh lebih beragam (118 nama unik) dan natural. Setelah variasi diwajibkan menulis pesan baru, hanya 2/50 lolos karena 42 variasi tetap menyalin teks sumber.
- GPT-6 Astra (OpenAI, run 25 September) menulis ulang pesan utama di 81/81 variasi.

Pelajaran: model Claude cenderung menyalin teks sumber jika teks itu dikirim. Rencana perbaikan: job variasi tidak lagi membawa teks sumber, cukup label intent, deskripsi kasus, dan ringkasan topik.

Pembaruan: job variasi kini tidak membawa teks sumber (hanya label, kasus, dan topik game), dan Bedrock memakai ConverseStream agar koneksi panjang tidak diam lalu diputus jaringan. Opus 4.6 dua kali gagal tanpa streaming (koneksi putus, lalu tanpa respons 30 menit).

Trial Sonnet 4.6 dengan streaming dan tanpa teks sumber (50 job yang sama, USD 0,34, 196 detik): 34/50 lolos, 0 variasi menyalin sumber, 123 nama unik, 22/261 kalimat konteks terulang, "gw" 1/311. Pemeriksaan manual 12 contoh yang lolos: bahasa natural, tetapi sekitar 3 label janggal, terutama pesan yang isinya meragukan/menyudutkan tetapi diberi label defend agar sama dengan label sumber, dan pemain yang menolak tuduhan terhadap dirinya diberi label neutral. Prompt kini menegaskan makna pesan harus sesuai label; sebutan yang sama dengan nama asli diabaikan, bukan ditolak.

## Alur manual lewat ChatGPT/Gemini, 26 September 2026

Tanpa API: label_target_manual.py membuat prompt, lalu jawaban dari chat web divalidasi dengan validate_session dan disimpan dalam format checkpoint yang sama.

~~~powershell
.\venv\Scripts\python.exe lama/generateDataset/label_target_manual.py prompts --dir ai_2_dataset_baru/data/manual_pilot_25 --per-case 25 --batch-size 10
# tempel prompt/prompt_001.txt ke ChatGPT/Gemini, simpan jawaban sebagai hasil/001_chatgpt.txt atau hasil/001_gemini.txt
.\venv\Scripts\python.exe lama/generateDataset/label_target_manual.py import --dir ai_2_dataset_baru/data/manual_pilot_25
.\venv\Scripts\python.exe lama/generateDataset/label_target_manual.py export --dir ai_2_dataset_baru/data/manual_pilot_25 --output ai_2_dataset_baru/data/dataset_final3_context_target_pilot25.csv
~~~

Nama file hasil menentukan kolom model di laporan (bagian setelah garis bawah pertama). Beberapa file untuk batch yang sama boleh ada; sesi valid pertama per job yang dipakai. import menulis laporan.md dan prompt_ulang/ untuk job yang gagal beserta alasannya. Pilot 25 per kasus: 775 job dalam 78 prompt.
