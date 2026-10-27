"""Bahan dialog pendukung; intent konteks ditentukan dari teks sendiri."""
AMBIG = '''
{a} dan {b} sama-sama baru mengirim jawaban setelah jeda panjang.
dua nama yang sedang dibahas itu {b} serta {a}, catatannya belum dipisah.
{a} dan {b} masing-masing mengganti pilihan vote satu kali.
aku mencatat {b} dan {a} sama-sama mengaku Spy.
catatan soal jeda chat ini berlaku buat {a} maupun {b}.
{b} juga {a} menulis hasil Peek tanpa nomor ronde.
{a} dan {b} keduanya belum memberikan rincian aksi malam.
yang sedang dibahas bersamaan: {b} dan {a}, masing-masing mengulang klaimnya.
{a} serta {b} sama-sama menulis pesan sebelum waktu diskusi tersisa separuh.
dua klaim Stalker itu datang dari {b} dan {a}.
aku punya dua catatan dengan urutan serupa, satu buat {a}, satu buat {b}.
{b} maupun {a} belum menyebut kapan pilihan vote berubah.
{a} dan {b} mengirim penjelasan soal koneksi di ronde yang sama.
catat {b} dan {a} sebagai dua orang yang sama-sama belum membuka role.
{a} serta {b} masing-masing menulis dua versi urutan malam.
{b} dan {a} sama-sama meminta pembahasan hasil skill dulu.
dua pesan pendek itu milik {a} dan {b}; isinya sama-sama klaim Civilian.
{b} juga {a} sudah menulis jawaban tentang alasan menunggu.
{a} dan {b} masing-masing berhenti mengetik saat topik vote muncul.
yang belum selesai menjelaskan urutan chat ada dua, {b} dan {a}.
{a} serta {b} sama-sama menyebut bahwa chatnya sempat terkunci.
{b} dan {a} masing-masing melaporkan hasil skill tanpa nama role lengkap.
ada dua klaim yang ingin dibahas bersama, dari {a} dan {b}.
{b} maupun {a} mengubah keterangan soal malam pertama.
{a} dan {b} sama-sama mengusulkan agar vote diselesaikan sekarang.
'''.strip().splitlines()

PAIR_FOLLOW = '''
dua nama itu masih kita bahas bareng, belum dipilih salah satunya.
catatan keduanya belum kupisah ke bagian masing-masing.
untuk dua orang itu, urutan chatnya masih kubaca bersebelahan.
aku masih mencatat keduanya dalam satu pembahasan.
dua klaim tersebut belum kita urutkan satu per satu.
'''.strip().splitlines()

SELF_CONTEXT = '''
{a} mengaku Spy, sedangkan {b} belum menulis role.
{b} bertanya soal nomor ronde; {a} sedang menyalin catatan vote.
aku mencatat pilihan {a} dan {b} sebelum pembahasan dilanjutkan.
{a} memakai kata Guard pada pesannya, {b} hanya menulis nama role.
{b} dan {a} sudah mendapat giliran menjelaskan; sekarang lanjut ke peserta lain.
'''.strip().splitlines()

ACCUSATIONS = '''
{s}, aku curiga kamu Hitman karena belum menjawab sejak tadi.
aku vote {s}, diamnya seperti sedang menyembunyikan sesuatu.
klaim {s} terdengar palsu, aku nggak percaya role yang disebutnya.
{s} paling sus buatku, jeda jawabnya terasa sengaja dibuat.
aku menduga {s} yang melakukan Hostage, ceritanya belum meyakinkan.
{s}, alasan terlambatmu janggal menurutku, aku pilih vote kamu.
jangan percaya {s}, klaimnya kelihatan seperti alibi palsu.
yang kucurigai {s}; tidak menjawab pertanyaan aksi itu aneh.
aku mau mengeluarkan {s}, pola jawabnya seperti Hitman cari aman.
{s} pasti menutup sesuatu, aku nggak percaya diamnya cuma kebetulan.
'''.strip().splitlines()

ROLE_CLAIMS = '''
aku mengaku Spy dan akan menulis catatan aksi setelah ini.
aku Stalker, hasil skill akan kutuliskan terpisah.
role-ku Civilian, aku ingin mencatatnya dulu di chat.
aku memakai Guard pada malam kedua menurut catatanku.
aku menyebut role Stalker untuk dicatat pada ronde ini.
'''.strip().splitlines()

REQUESTS = '''
{s}, boleh beri penilaian tentang klaim role-ku tadi?
aku menunggu pendapatmu soal alibiku, {s}.
{s}, bagaimana penilaianmu terhadap catatan aksiku?
aku minta kamu menanggapi klaimku, {s}, setelah membacanya.
{s}, bisa komentari penjelasan yang kuberikan soal urutan malam?
'''.strip().splitlines()

TIMERS = '''
buat semuanya, timer diskusi menunjukkan empat puluh detik.
sebentar, sisa waktunya satu menit di layarku.
pengingat untuk semua: ronde belum berganti, masih sesi diskusi.
jam diskusi sudah berjalan, sisa tiga puluh detik.
untuk seluruh pemain, waktu vote akan mulai setelah hitungan ini.
'''.strip().splitlines()

# Setiap utas: 1 pembuka dengan nama + 11 lanjutan substantif.
# Pertanyaan eksplisit ke kelompok, sehingga jawaban tidak menarget penanya tertentu.
THREADS = [
('catatan urutan aksi {a} belum diberi nomor malam.', '''
buat semua, kita pakai nomor malam dari awal permainan atau setelah ronde pembuka?
di catatanku, malam pertama dihitung sesudah diskusi pembuka.
aku memakai hitungan yang sama untuk daftar aksi.
kalau begitu kolom tanpa nomor jangan langsung dimasukkan ke malam kedua.
ada yang punya urutan pesan sebelum transisi ronde? Tolong tulis waktunya saja.
di layar tercatat pesan masuk sebelum transisi, tetapi baru kubaca setelahnya.
waktu diterima dan waktu dibaca memang dua catatan terpisah.
aku akan taruh keduanya di kolom berbeda supaya tidak tertukar.
urutan yang kita bahas masih catatan klaim, belum kepastian aksi sebenarnya.
setuju, nama role yang diklaim juga perlu dipisah dari waktu pesan.
oke, nomor malam sudah bisa dibaca dengan aturan yang sama sekarang.
'''),
('pada catatan vote, {a} mengganti pilihan sebelum hitungan terakhir.', '''
untuk semua yang mencatat, perubahan pilihan ini terjadi sebelum atau sesudah tombol dikunci?
aku merekamnya sebelum kunci vote muncul.
angka di layar saat itu masih bisa berubah.
berarti daftar sementara jangan disebut hasil akhir dulu.
ada yang ingat berapa kali layar diperbarui? Pertanyaannya untuk siapa pun yang lihat.
aku lihat dua pembaruan pada jeda yang sama.
dua pembaruan layar belum memberi jumlah pemain yang mengganti pilihan.
iya, kita hanya mencatat tampilan yang terlihat.
hasil akhir baru muncul sesudah hitungan berhenti.
aku pisahkan catatan sebelum kunci dan sesudah kunci.
sekarang kronologi perubahan tampilannya sudah jelas untuk dibaca bersama.
'''),
('pesan {a} tentang hasil Peek tertulis tanpa tanda baca.', '''
semua yang membaca, kita salin teks hasilnya dulu atau tafsiran masing-masing?
aku memilih menyalin teks yang terlihat terlebih dahulu.
bagian sebelum titik dua itu pengantar klaim, sesudahnya hasil yang dilaporkan.
format di chat mungkin tidak menyimpan pergantian baris.
ada yang melihat baris aslinya? Tolong jawab ke grup tanpa menyebut tebakan role.
aku lihat satu baris saja, tetapi ada spasi panjang di tengah.
spasi itu akan kutandai, belum kuterjemahkan jadi dua hasil.
aku juga memisahkan kata Peek dari nama role dalam catatan.
klaim hasil masih harus dibaca sebagai ucapan pemain, bukan pengumuman sistem.
iya, catatan grup akan memakai tanda kutip untuk laporan tersebut.
teksnya sudah tersalin, setelah ini kita bisa membahas maknanya.
'''),
('klaim Spy {a} ditulis sebelum pembahasan aksi malam dibuka.', '''
buat semuanya, mari bedakan jam klaim role dan jam laporan aksi.
klaim role hanya menyebut identitas yang diakui.
laporan aksi menambahkan malam dan jenis skill yang disebut.
aku membuat dua kolom agar urutannya tidak menyatu.
ada yang mencatat kapan sesi tanya aksi dimulai? Siapa pun boleh jawab.
di layar, sesi tanya baru berjalan setelah tiga pesan berikutnya.
aku punya urutan tampilan yang sama.
jadi jam membaca klaim bukan otomatis waktu skill digunakan.
catatan ini akan memakai waktu pesan untuk chat saja.
untuk aksi malam, nomor malam tetap ditulis terpisah.
oke, batas antara klaim role dan laporan aksi sudah kita sepakati.
'''),
('chat {a} sempat terpotong pada bagian penjelasan ronde.', '''
untuk semua pembaca, potongan yang terlihat berakhir di kata apa?
layarku berhenti setelah kata malam, belum ada angkanya.
aku juga belum melihat angka pada baris itu.
ada pesan lanjutan masuk, tetapi posisinya terpisah oleh beberapa balasan.
ada yang sempat menyalin urutannya? Tolong kirim bagian teks, bukan kesimpulan.
salinanku punya dua baris dengan jarak waktu beberapa detik.
kita catat dua baris itu sebagai dua waktu kirim dahulu.
belum ada alasan teknis yang tercantum di potongan pertama.
aku akan beri tanda bahwa bagian angka baru muncul di baris lanjutan.
catatan yang belum lengkap jangan ditambah kata hasil tebakan.
oke, potongan teks dan sambungannya sudah tertata untuk dibaca ulang.
'''),
('di ringkasan diskusi, {a} menyebut chat terkunci selama jeda.', '''
buat seluruh grup, apakah waktu chat terkunci dicatat terpisah dari transisi malam?
aku menaruhnya sebagai peristiwa tampilan, bukan penanda role.
di catatanku juga hanya tertulis akses chat berubah.
identitas korban tidak menjadi pengumuman publik yang bisa kita salin.
ada yang ingat jeda tampilannya? Silakan jawab kalau memang melihat.
layarku memperlihatkan ikon kunci lalu kembali ke kolom ketik.
aku tidak sempat menulis durasi persis, hanya urutan ikonnya.
urutan itu bisa disimpan tanpa menambahkan dugaan penyebab.
nama skill yang disebut pemain tetap masuk kolom klaim.
status layar masuk kolom pengamatan, keduanya beda jenis catatan.
baik, bagian yang terlihat dan bagian yang diklaim sudah dipisah sekarang.
'''),
('ada dua penulisan nomor ronde pada catatan {a}.', '''
semua yang menyusun ringkasan, tolong pastikan malam dan ronde tidak dianggap satu nomor.
aku menyimpan nomor malam dalam kolom aksinya.
nomor ronde diskusi ada di kolom lain pada catatanku.
kalau dua jenis nomor digabung, urutan akan sulit dibaca.
ada yang masih menyimpan format awal? Tolong jelaskan judul kolomnya ke grup.
format awal cuma punya satu judul waktu tanpa membedakan jenisnya.
aku akan menambahkan judul yang lebih jelas pada salinanku.
angka lama tetap disimpan apa adanya dulu.
koreksi format tidak berarti kita sudah memilih versi cerita tertentu.
iya, kedua penulisan akan tetap tampak di ringkasan.
sekarang kita bisa membaca perbedaannya tanpa tertukar jenis nomor.
'''),
('pengakuan Stalker {a} belum menyertakan nama target Peek.', '''
buat semua, mari pisahkan pernyataan role dari rincian hasil skill.
aku mencatat role yang diakui pada bagian pertama.
bagian hasil masih berupa ruang untuk teks laporan berikutnya.
klaim saja tidak menyebut siapa yang diperiksa.
apakah ada teks hasil di pesan lanjutan? Siapa pun yang membaca boleh menyalinnya.
di salinanku belum ada teks hasil pada urutan itu.
aku tandai kosong, bukan menambahkan nama dari dugaan.
nama target skill dan pemain yang mengirim laporan harus berada di kolom berbeda.
iya, supaya nama pengirim tidak terbaca sebagai hasil Peek.
urutan pesan tetap kita pertahankan ketika menulis ringkasannya.
catatan role dan bagian yang belum dilaporkan sudah jelas terpisah.
'''),
('alasan perpindahan vote {a} disebut setelah daftar pilihan dibacakan.', '''
untuk semua pencatat, kapan daftar sementara dibuka di layar?
di layarku setelah pembahasan aksi malam selesai.
aku juga baru melihat daftar pada bagian itu.
alasan memilih ada di chat, sedangkan pilihan tercatat di tampilan vote.
ada yang menyimpan urutan keduanya? Tolong bagikan urutan saja kepada grup.
aku menulis tampilan daftar dulu, baru beberapa pesan alasan setelahnya.
ringkasanku akan memakai urutan tersebut untuk waktu chat.
isi alasan tetap disalin lengkap tanpa ditambah tafsiran.
perbedaan waktu membaca pesan tidak akan kuanggap sebagai perubahan pilihan.
iya, yang kita catat cuma kapan informasi itu terlihat.
sekarang daftar pilihan dan alasan tertulis bisa dibandingkan tanpa tercampur.
'''),
('laporan Guard {a} mencantumkan kata aman tanpa penjelasan tambahan.', '''
buat semua, kita perlu menulis hasil laporan persis sebelum membuat ringkasannya.
aku menyimpan kata aman sebagai kutipan, belum menggantinya dengan nama role.
laporan Guard tidak sama dengan laporan Peek.
jenis skill pada catatan harus tetap terlihat.
ada yang punya versi teks lengkap? Tolong salin ke grup kalau ada.
salinanku hanya menambahkan keterangan tadi malam di bagian akhir.
berarti bagian waktu bisa dicatat tanpa mengubah kata hasilnya.
aku membuat kolom skill supaya dua jenis laporan tidak tertukar.
klaim pemain tetap klaim, kita belum memperoleh kepastian role dari sistem.
iya, jangan menaruh kata Civilian kalau tidak tertulis dalam laporan itu.
kutipan hasil dan jenis skillnya sudah selesai dirapikan di catatan.
'''),
]
