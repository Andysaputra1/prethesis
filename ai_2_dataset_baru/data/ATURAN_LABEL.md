# Aturan Label Intent dan Target (relabel 26 Oktober 2026)

Aturan ini dipakai untuk melabel ulang `dataset_final3.csv` (Model 1, intent) dan
`dataset_final3_context_target_pilot25_lengkap.csv` (Model 2, target). Tujuannya: kalimat yang mirip
mendapat label yang sama, dan arti label sama dengan cara bot di game memakainya
(`INTENT_AKSI`: ungkap/tuduh/klaim_palsu = offend, bela_diri/bela_orang/info_sandera = defend,
jawab/ajak_bicara/tanya_info = neutral).

Log perubahan per baris ada di `relabel_2026-10-26.csv`. Label lama tetap ada di riwayat git.

## Prinsip

- **Intent dinilai dari efek pesan terhadap kecurigaan atau vote ke pemain.** Menaikkan kecurigaan =
  offend, melindungi dari kecurigaan = defend, tidak ke mana-mana = neutral.
- **Intent ditentukan dari teks pesan itu sendiri**, karena Model 1 hanya membaca teks. Pengecualian:
  pesan yang isinya hanya "setuju/iya/sama" terhadap pesan sebelumnya mengikuti sikap yang disetujui
  (konvensi kasus `agreement` di dataset target). Di dataset intent (tanpa konteks), pesan seperti itu
  tidak diubah.
- **Satu pesan hanya punya satu intent.** Jika ada unsur menuduh dan membela sekaligus, intent = offend.
  Relasi per pemain (bela A, tuduh B) dicatat lengkap oleh target Model 2.

## Intent: urutan keputusan

Periksa dari atas. Aturan pertama yang cocok menentukan label.

### 1. OFFEND: pesan menaikkan kecurigaan atau mendorong vote ke pemain atau kelompok

| Kode | Pola | Contoh |
| --- | --- | --- |
| O-a | Tuduhan atau kecurigaan langsung, ajakan vote/eksekusi | "aku curiga Budi", "dia pasti Hitman", "vote Tio aja", "kelakuan Yuda sus" |
| O-b | Hasil skill yang memberatkan | "aku Stalker, peek-ku bilang Lala Hitman", "Tio terindikasi jahat dari peek-ku" |
| O-c | Menyerang kredibilitas pemain | "jangan percaya F", "klaim Spy dia palsu", "dia ngarang", "info kalian terlalu rapi" |
| O-d | Pertanyaan yang menyiratkan kesalahan (ada sindiran/kecurigaan) | "kalau memang Spy, kenapa nggak bilang siapa yang dijaga? jangan-jangan ngarang", "lu ngaku civilian, kok tahu siapa yang aman?", "kamu diam terus, apa karena tahu target Guard?" |
| O-e | Mengalihkan kecurigaan ke orang/kelompok lain | "coba cek dulu pergerakan si C", "curigai yang pasif saja", "yang panik malah yang lempar tuduhan duluan", "lihat siapa yang pertama menyebarkan tuduhan" |
| O-f | Minta divote diri sendiri dengan pasrah/tulus (konvensi kasus `self`) | "kalau kalian curiga, vote aku saja biar cepat" |
| O-g | Campuran: ada bagian membela **dan** bagian O-a sampai O-f | "aku bukan Hitman, justru Andi yang aneh", "tadi malam gw nggak ngapa-ngapain, coba cek si C", "Doni bersih, Wawan yang layak di-vote" |

Pertanyaan menekan tanpa sindiran (O-d tidak terpenuhi) **bukan** offend; lihat N-b.

Batas tambahan:
- **Sasaran harus jelas.** Sasaran bisa berupa nama, kata ganti, atau ciri kelompok ("yang paling sering
  mengarahkan vote", "yang pasif", "yang nuduh gw"). "Cek pemain lain aja" atau "tanya yang lain dulu"
  tanpa ciri tidak dihitung O-e. Ajakan memeriksa tanpa ciri curiga ("coba perhatikan jawaban mereka",
  "baca lagi pesannya") = neutral.
- **Mengkritik tuduhan vs menyerang penuduh.** Mengkritik isi tuduhan ("tuduhan itu ngawur", "cuma
  diulang-ulang", "jangan putarbalikkan ucapanku") = D-d. Menyerang konsistensi, motif, atau perilaku
  si penuduh ("yang nuduh aku malah berubah-ubah", "timing tuduhan ini pas banget buat nutupin pelaku")
  = O-c, jadi pesan yang juga membela diri menjadi O-g.
- **Mengkritik cara berpikir kelompok** ("mereka cuma ikut arus vote") = O-c.
- **Inkonsistensi penuduh.** Pesan yang membela diri/orang lain sambil menunjuk penuduh berganti-ganti
  sasaran ("kamu dari tadi menuduh aku, sekarang tiba-tiba menuduh Farah") = O-g. Kalimat fakta yang
  berdiri sendiri tanpa membela dan tanpa penilaian ("Tomi tadi menuduh Rafi, sekarang Umar") = neutral.
- **Motif penuduh.** Menyebut motif yang menyiratkan penuduh pelaku atau sedang menutupi pelaku = O-c.
  Motif biasa ("karena aku beda pendapat", "karena aku menyanggah teorinya") = D-d.
- **Penilaian vs fakta.** Menunjuk kontradiksi atau meragukan klaim **dengan** penilaian curiga ("aneh",
  "janggal", "nggak cocok", "mencurigakan", "ngarang", "bohong", "palsu", "nggak masuk akal") = offend.
  Tanpa penilaian ("jawaban itu beda dari jawaban pertamamu", "itu baru klaim, belum bisa dipastikan",
  "siapa pun bisa ngaku Spy") = neutral.
- **Pernyataan umum tentang Hitman** tanpa menunjuk perilaku pemain di chat ("Hitman emang suka lempar
  tuduhan palsu") = neutral. Menunjuk perilaku yang terlihat di chat dengan penilaian curiga ("waspada
  sama pola main kayak gini", "mencurigakan banget cara main kayak gitu") = offend.

### 2. DEFEND: tidak ada unsur offend, dan pesan melindungi pemain dari kecurigaan atau vote

| Kode | Pola | Contoh |
| --- | --- | --- |
| D-a | Menyangkal untuk diri sendiri | "aku bukan Hitman", "sumpah aku bukan pelakunya", "aku nggak bersalah" |
| D-b | Klaim role yang dipakai membela diri: klaim + sangkalan, menolak divote, atau menjawab tuduhan | "saya bukan hitman, saya stalker dan siap diverifikasi", "kalian boleh curiga, tapi role aku Civilian", "jangan vote aku, aku Spy" |
| D-c | Membersihkan pemain lain | "Budi bukan Hitman", "si E aman", "peek-ku: Vina bukan Hitman", "jangan vote Dika" |
| D-d | Membantah tuduhan tanpa menuduh balik | "tuduhanmu nggak ada buktinya", "lu nuduh gw karena apa?", "jangan asal cap gw Hitman" |
| D-e | Menjelaskan perilaku yang dicurigai agar tidak dicurigai | "aku telat karena koneksi", "dia diam karena lagi lag" |
| D-f | Sarkasme atau tantangan yang menyiratkan tuduhan itu salah | "aku Hitman kalau kalian percaya omongan itu", "silakan vote aku, nanti kalian nyesel" |
| D-g | Menanggapi tuduhan ke orang tertentu dengan meminta jangan buru-buru | "lu boleh curiga, tapi jangan eksekusi orang cuma karena feeling" |

### 3. NEUTRAL: sisanya

| Kode | Pola | Contoh |
| --- | --- | --- |
| N-a | Klaim role/informasi tanpa sangkalan, tanpa membela, tanpa menuduh | "aku klaim Civilian ya, biar jelas", "aku Spy, semalam guard orang yang tepat" |
| N-b | Pertanyaan meminta info tanpa sindiran, walau mendesak | "Spy, semalam guard siapa?", "siapa yang lu Guard tadi malam? jawab simpel aja" |
| N-c | Logistik, teknis, waktu, aturan game | "sisa waktu berapa?", "chat dikunci lagi" |
| N-d | Ajakan umum tanpa sasaran dan bukan tanggapan atas tuduhan tertentu | "kumpulkan bukti dulu sebelum vote" |
| N-e | Setuju/menanggapi tanpa sikap ke pemain | "oke", "hmm bisa jadi", "ayo bahas lagi" |
| N-f | Hasil skill yang tidak memberatkan dan tidak membersihkan | "aku peek Raka, dia bukan Spy" |

Bedakan D-g dan N-d: D-g menanggapi kecurigaan ke orang tertentu ("lu boleh curiga, tapi…") atau
melindungi kelompok berciri ("jangan eksekusi berdasarkan siapa yang paling vokal"). N-d adalah nasihat
umum tanpa sasaran sama sekali ("kumpulkan bukti dulu sebelum vote").

Peringatan dibedakan dari sasarannya:
- Menegur tindakan menuduh ("udah, jangan langsung nuduh", "kalian nuduh tanpa bukti", "jangan asal ngajak
  orang vote dong") = D-d. Teguran ini melindungi yang sedang dituduh.
- Hati-hati soal proses memutuskan ("kumpulin info dulu, jangan asal vote", "bahaya kalau kita membuang
  civilian", "jangan cuma pakai feeling", "jangan asal memutuskan dulu") = N-d.

Koreksi diri tanpa sangkalan ("aku salah ingat", "tadi salah ketik") = neutral.

Pesan "setuju/iya/bener" **yang ditambah isi sendiri** dinilai dari isinya. Hanya pesan yang isinya
sekadar setuju yang mengikuti sikap pesan yang disetujui. Pengecualian: pesan utama kasus `agreement`
di dataset target tetap mengikuti sikap yang disetujui, karena itulah yang diuji kasus tersebut.

Keputusan tambahan dari pass relabel (supaya chunk yang dikerjakan terpisah tetap seragam):
- "Siapa yang (paling) diuntungkan" dan "giliran si X menjelaskan" setelah membela diri dihitung sasaran berciri (O-e/O-g).
- Klaim role + menolak desakan ("jangan tuntut aku punya hasil Peek", "jangan paksa aku kasih info palsu")
  = D-b, karena menjawab keraguan.
- Penjelasan perilaku sendiri dengan penanda pembenaran ("makanya aku diam", "jadi wajar aku nanya", "bukan sengaja")
  = D-e.
- Alasan koneksi/sinyal/lag untuk telat, diam, atau pesan terpotong milik sendiri ("maaf, tadi koneksiku putus",
  "sinyalku jelek banget") = D-e, walau tanpa sangkalan. Ini konvensi mayoritas dataset target (55 defend).
  Pertanyaan atau komentar umum soal koneksi ("koneksi kalian aman?", "bisa karena koneksi juga") = neutral.
- Hasil Peek "bukan warga biasa/bukan civilian" tanpa kata Hitman = neutral (N-f). Spy menyebut target
  guard "aman/selamat" = neutral (selamat dari serangan, bukan bersih).
- Memvalidasi klaim role baik pemain lain ("klaim Spy si Bimo paling masuk akal") = D-c.

Kata pembuka seperti "santai", "serius", "tenang", "sumpah" sebelum klaim role tidak cukup untuk D-b. Klaim menjadi
D-b bila ada sangkalan, penolakan divote, atau jawaban atas keraguan ("mau percaya atau nggak terserah
kalian", "kalian boleh curiga, tapi…").

## Target (khusus dataset target, Model 2)

- **Offend/defend:** target = setiap pemain yang dituduh (offend) atau dilindungi (defend), termasuk diri
  sendiri saat membela diri. Pesan campuran mencatat kedua relasi. Bila acuannya tidak jelas, pakai
  `tidak_diketahui` dengan relasi sesuai intent. Pesan offend/defend tidak memakai relasi neutral.
- **Nama yang disebut belum tentu target.** Saksi/sumber ("dari cerita Citra…"), orang yang disetujui
  ("sepemikiran dengan Nina…"), dan orang yang diajak bicara dalam pesan offend/defend bukan target,
  kecuali dia juga dituduh atau dibela.
- **Neutral:** relasi neutral untuk
  1. pemain lain yang disebut nama atau panggilannya, atau dirujuk "dia/-nya" yang jelas orangnya dari konteks;
  2. pemain yang disapa "kamu/lu/-mu" dan bisa dipastikan dari konteks;
  3. pemain yang pertanyaan atau ucapannya **kepada pengirim** sedang dijawab langsung.
  Pesan untuk semua orang ("ada yang…", "kalian…") tanpa target. Jawaban atas pertanyaan yang ditujukan ke
  semua orang ("koneksi kalian lancar?" → "koneksiku lancar") juga tanpa target.
- **Konvensi yang dipertahankan:** `first_message_unknown` (kata ganti tanpa konteks) tetap
  `tidak_diketahui`; kasus `self` ("vote aku saja") tetap offend ke diri sendiri.
- Bila intent berubah, target disesuaikan: neutral → defend/offend diberi target sesuai aturan di atas;
  offend/defend → neutral memakai aturan neutral.
