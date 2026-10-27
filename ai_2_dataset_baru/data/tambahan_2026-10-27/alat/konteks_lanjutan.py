"""40 utas tambahan yang ditulis terpisah agar reference_start memiliki 50 riwayat berbeda.
Setiap utas: pembuka bernama, lalu 11 pesan neutral tentang bukti/proses ke grup.
Tidak ada rujukan pemain baru di sela-sela topik awal.
"""
EXTRA = [
('jawaban {a} tentang malam tadi muncul setelah pergantian fase.', '''
bentar, fase berganti saat pesan diketik atau saat masuk?
buat semua yang lihat, yang tercatat di layar cuma waktu masuknya.
aku nggak punya catatan waktu mulai mengetik.
kalau begitu kita jangan menyamakan keduanya dulu.
pesan panjang bisa mulai ditulis sebelum hitungan selesai.
pesan pendek juga belum tentu dibaca tepat saat masuk.
yang bisa dibandingkan sekarang urutan tampilnya saja.
iya, aku masih punya salinan urutannya.
transisi fase berada di antara dua baris terakhir.
aku menandai titik transisi itu untuk grup.
oke, sekarang bagian sebelum dan sesudah transisi sudah terpisah.
'''),
('aku membaca laporan {a} yang menyebut dua malam sekaligus.', '''
semua, kita bahas satu malam dulu biar nggak lompat-lompat.
mulai dari malam pertama sesuai urutan permainan saja.
laporan yang menyebut dua waktu bisa dipecah jadi dua bagian.
aku sedang memisahkan kalimatnya tanpa mengganti isi.
buat grup, kata sesudah itu di sini menghubungkan dua kejadian.
berarti tidak perlu dibaca seolah terjadi bersamaan.
ya, urutan tulisan dan urutan kejadian perlu dibedakan.
aku punya catatan awal yang masih satu paragraf.
bagian sebelum koma masuk urutan pertama.
sisanya masuk urutan berikutnya sesuai teks.
sekarang dua bagian itu bisa kita nilai dengan urutan yang sama.
'''),
('pesan {a} soal pilihan vote memakai kata nanti.', '''
nanti itu belum menunjukkan vote sudah masuk, ya.
untuk semua, aku bedakan rencana di chat dengan pilihan di layar.
aku juga belum menaruh pesan rencana di kolom hasil.
ada jeda sebelum tombol vote tersedia.
jadi ucapan saat diskusi bisa mendahului kesempatan memilih.
kalau perlu, kita beri tanda rencana pada bagian itu.
iya, teksnya masih tetap disimpan apa adanya.
aku lihat daftar pilihan baru muncul setelah diskusi ditutup.
urutan itu cocok dengan tampilan di layarku.
hasil final baru bisa dibaca sesudah seluruh hitungan selesai.
baik, yang di chat kita baca sebagai rencana dahulu.
'''),
('di pesan {a} ada kata bukan sebelum nama role.', '''
aku mau salin kalimat lengkap, jangan cuma kata terakhirnya.
buat semuanya, kata negasi di sini perlu tetap ikut.
iya, potongan satu kata bisa mengubah apa yang tertulis.
aku menulis ulang mulai dari awal kalimat.
kalimatnya berakhir sebelum baris berikutnya.
berarti kata bukan masih berada pada klausa yang sama.
yang membaca dari notifikasi mungkin cuma melihat ujungnya.
di chat lengkap bagian awalnya masih terlihat.
aku pakai teks chat untuk salinan grup.
notifikasi tidak akan kupakai menggantikan isi pesan.
oke, kalimat utuhnya sudah tersedia untuk kita bahas.
'''),
('klaim {a} dikirim dua kali dengan jarak beberapa detik.', '''
buat semua, apakah teks kedua sama persis atau ada tambahan?
yang kulihat, teks kedua menambahkan nomor malam.
bagian role di keduanya tertulis sama.
aku belum menggabungkannya jadi satu baris.
pengiriman ulang bisa dicatat sebagai kejadian terpisah.
iya, jangan menghapus salah satu dari urutan chat.
tambahan nomor tetap bisa kita baca di pesan kedua.
aku beri penanda versi pertama dan versi berikutnya.
label versi itu cuma penanda waktu salinan.
isinya belum aku simpulkan sebagai koreksi atau penegasan.
sekarang kedua teksnya bisa dibandingkan langsung.
'''),
('hasil skill dalam pesan {a} ditulis memakai singkatan.', '''
buat grup, kita punya kepanjangan yang tertulis atau cuma singkatan ini?
aku hanya melihat singkatan pada salinan chat.
kalau begitu jangan diganti dulu jadi nama role tertentu.
aku simpan hurufnya persis seperti pesan.
huruf besar dan kecil tetap akan terlihat.
ada spasi di antara pengantar dan hasilnya.
iya, spasi itu bisa dicatat tanpa mengubah kata.
aku belum melihat penjelasan tambahan setelahnya.
bagian yang belum dijelaskan kita tandai terbuka.
selanjutnya pembahasan bisa pakai teks asli, bukan tebakan kepanjangan.
oke, salinan sudah sesuai dengan yang tampil di chat.
'''),
('catatan {a} memakai kata kemarin untuk aksi malam.', '''
buat semuanya, kemarin di chat game bisa berarti ronde sebelumnya.
iya, belum tentu tanggal kalender yang sedang dibicarakan.
aku mau menyamakan istilah waktunya dulu.
di urutan permainan ada malam lalu dan malam yang baru selesai.
dua istilah itu kita pisahkan sementara.
kata kemarin tetap dibiarkan dalam kutipan aslinya.
aku beri kolom untuk nomor malam kalau nanti dijelaskan.
sekarang kolom itu belum diisi dengan tebakan.
pesan sesudahnya tidak menambahkan angka.
berarti informasi waktu yang tersedia memang masih seperti ini.
baik, kita bahas dengan batas informasi tersebut.
'''),
('jawaban {a} masuk di antara dua pertanyaan grup.', '''
pertanyaan pertama tentang role, yang berikutnya tentang waktu skill.
semua yang mencatat, tolong pertahankan urutan kedua pertanyaan.
aku tidak akan menempelkan jawaban ke yang paling dekat saja.
isi jawabannya perlu dibaca lengkap terlebih dahulu.
ada kata malam di tengah kalimat.
ada juga nama role pada bagian awal.
jadi satu pesan bisa memuat dua jenis informasi.
aku pecah bagian role dan bagian waktu di catatan.
dua bagiannya tetap memiliki jam kirim yang sama.
iya, pemisahan catatan tidak mengubah urutan pesan asli.
sekarang kita bisa membaca jawabannya tanpa kehilangan kedua pertanyaan.
'''),
('laporan {a} menyebut chat terbuka kembali sebelum vote.', '''
bisa kita cocokkan transisi layar tanpa menebak penyebabnya dulu.
buat semua, apakah kolom ketik sudah muncul sebelum tombol vote aktif?
di layarku kolom ketik lebih dulu terlihat.
aku mencatat urutan tampilan yang sama.
nomor detiknya tidak sempat kusimpan.
berarti kita punya urutan, bukan durasi pasti.
durasi jangan diisi angka perkiraan dalam kutipan.
aku menambahkan tanda belum tercatat pada bagian detik.
status akses chat tetap terpisah dari klaim role.
iya, perubahan tampilan saja tidak menyebut identitas korban.
oke, urutan yang memang terlihat sudah kita catat.
'''),
('keterangan {a} tentang Guard memakai kalimat pasif.', '''
buat grup, aku ingin baca subjek kalimatnya dengan teliti.
kalimat pasif tidak selalu menempatkan pelaku di awal.
di teks ini nama role muncul sesudah pengantar.
aku akan mempertahankan susunan aslinya pada catatan.
bagian yang menyebut aksi jangan dipindah jadi pengakuan role.
iya, dua informasi itu tidak otomatis sama.
belum ada kalimat lanjutan yang menambahkan penjelasan.
aku menandai bahwa bacaan kita masih berdasarkan satu pesan.
kalau nanti ada tambahan, urutannya bisa dilanjutkan.
untuk sekarang teks utuh lebih baik ditampilkan.
silakan lanjut menilai dengan kalimat yang sudah tersalin ini.
'''),
('ada koreksi angka pada pesan {a} tentang penggunaan skill.', '''
yang dikoreksi angka, bagian nama skill masih sama.
buat semua, kita catat versi sebelum koreksi juga.
aku masih menyimpan salinan baris pertamanya.
baris berikutnya datang dengan tanda bintang di depan angka.
itu bentuk koreksi tertulis yang terlihat di chat.
alasannya belum disebut pada pesan yang sama.
aku tidak akan menambahkan alasan sendiri ke ringkasan.
jam kedua pesan tetap bisa dibandingkan.
keduanya masuk sebelum diskusi ditutup.
iya, urutannya tidak terpotong oleh pergantian fase.
sekarang koreksi dan teks awal bisa dibaca berdampingan.
'''),
('laporan {a} tentang Peek baru memuat bagian pengantar.', '''
buat semuanya, kita belum punya isi hasil pada bagian itu.
kalimat yang ada hanya menyebut akan melaporkan.
aku tandai sebagai pengantar, bukan hasil selesai.
ada baris kosong sesudahnya di salinan chat.
baris kosong itu tidak berisi nama role.
iya, jangan menambahkan hasil dari perkiraan.
aku masih membaca apakah ada pesan lanjutan di urutan berikutnya.
yang terlihat setelahnya pengumuman waktu diskusi.
jadi belum ada tambahan hasil di bagian yang sedang dibaca.
catatan kita bisa berhenti pada informasi yang tersedia.
baik, pengantar dan hasil yang belum ada tetap dibedakan.
'''),
('pesan {a} soal malam sebelumnya memakai tanda kutip.', '''
untuk semua pembaca, bagian dalam kutip sebaiknya disalin utuh.
bagian di luar kutip menjadi komentar setelahnya.
aku sedang memisahkan dua bagian itu di catatan.
tanda kutipnya mulai setelah kata laporan.
penutup kutip muncul sebelum keterangan waktu.
berarti keterangan waktu itu berada di luar kutipan.
iya, susunan tersebut akan kupakai pada salinan.
aku tidak mengubah kata-kata dalam bagian kutip.
bagian komentar juga tetap dicatat sesuai urutan.
dua bagian berbeda ini masih berasal dari pesan yang sama.
oke, sekarang batas kutipannya sudah terlihat jelas.
'''),
('penjelasan {a} tentang vote ditulis sebelum daftar akhir tampil.', '''
daftar akhir baru muncul setelah hitungan terakhir berhenti.
untuk semua, daftar sementara tadi masih bisa berubah.
aku punya salinan kedua tampilan itu.
judul salinannya akan dibedakan supaya tidak tertukar.
pilihan yang terlihat sementara bukan otomatis hasil final.
iya, teks pengantar di layar juga berbeda.
aku menambahkan waktu tampil untuk tiap salinan.
pesan diskusi berada sebelum kedua tampilan selesai.
berarti urutan baca tidak harus sama dengan urutan keputusan.
catatan akan tetap mengikuti waktu tampil yang terlihat.
baik, kita punya rujukan yang sama untuk pembahasan vote.
'''),
('aku menemukan kalimat bersambung dalam chat {a}.', '''
pesan pertama berhenti setelah kata tetapi.
semua yang membaca, jangan simpulkan klausa yang belum selesai dulu.
lanjutannya ada beberapa baris di bawah pada urutan chat.
aku sedang menyalin dua bagian itu tanpa menghapus pesan di antaranya.
bagian kedua diawali huruf kecil.
tetapi itu sendiri belum memberi kesimpulan penuh.
iya, isi lanjutannya masih perlu dibaca.
aku memberi garis penghubung pada salinan pribadi.
nomor urut masing-masing pesan tetap dipertahankan.
siapa pun bisa melihat potongan mana yang sudah lengkap.
oke, dua potongan sudah siap dibaca sebagai kalimat utuh.
'''),
('status yang ditulis {a} pada awal ronde masih berupa klaim role.', '''
buat grup, klaim dan pengumuman sistem berbeda sumber.
teks yang kita baca berasal dari kolom chat pemain.
aku mencatat sumbernya sebagai pesan, bukan hasil publik.
tidak ada pengumuman identitas korban yang bisa ditambahkan ke situ.
iya, kita hanya punya isi yang dituliskan.
format catatanku menaruh role yang diklaim dalam tanda kutip.
waktu pesan disimpan tepat di sebelah kutipan.
bagian hasil skill masih terpisah di bawahnya.
aku belum mengisi bagian hasil dengan kata dari klaim.
begitu lebih mudah membedakan informasi yang tersedia.
sekarang kita bisa menanggapi klaim tanpa mencampur sumbernya.
'''),
('di laporan {a}, urutan diskusi dan malam tertulis terbalik.', '''
aku sedang membaca apakah urutan tulisan memang dimaksudkan sebagai urutan kejadian.
buat semua, kalimat pertama dimulai dengan ringkasan ronde.
kalimat kedua baru menyebut kejadian malam.
ringkasan bisa saja ditempatkan sebelum rincian dalam sebuah pesan.
jadi posisi kalimat tidak otomatis sama dengan waktu kejadian.
aku tandai pengantar ringkasan secara terpisah.
kata sebelum dan sesudah tetap disalin persis.
iya, dua kata itu penting untuk membaca urutan waktu.
nomor malam juga tidak akan kutukar sendiri.
catatan lengkap akan mempertahankan susunan kalimat asli.
oke, kita bisa membahas urutannya dengan teks yang sudah jelas.
'''),
('jawaban {a} tentang skill belum memuat kata sudah atau belum.', '''
buat semuanya, bentuk kalimatnya belum menyebut apakah aksi selesai.
aku melihat nama skill dan nomor malam saja.
kalimat itu bisa disalin tanpa menambahkan status penggunaan.
iya, tambahan satu kata akan mengubah informasinya.
bagian yang kosong kita biarkan belum dijelaskan.
pesan sesudahnya membahas waktu diskusi.
berarti pada potongan ini tidak ada kelanjutan soal status aksi.
aku menaruh tanda tanya di kolom catatan pribadi, bukan di kutipan.
teks asli tetap tidak diberi tanda baca baru.
supaya semua bisa membedakan tulisan asli dengan catatan pembaca.
baik, informasi yang sudah dan belum ada bisa kita lihat bersama.
'''),
('nama skill dalam pesan {a} muncul setelah jeda tanda titik.', '''
kalimat pertama selesai sebelum nama skill muncul.
buat grup, kita jangan menyatukan dua kalimat itu tanpa membaca isinya.
aku menyalin titiknya sesuai chat.
kalimat kedua punya keterangan waktu sendiri.
jadi ada dua bagian yang dapat dibahas terpisah.
aku belum melihat kata penghubung di antara keduanya.
iya, kata penghubung tidak perlu kita karang.
kutipan akan mempertahankan pergantian kalimat itu.
nomor urut pesan tetap satu karena dikirim bersamaan.
catatan waktunya juga hanya satu waktu kirim.
sekarang kedua kalimat bisa dibaca dengan batas yang benar.
'''),
('catatan {a} menyebut vote yang belum dikunci.', '''
buat semua, fase memilih masih berjalan pada bagian itu.
di layar memang ada kesempatan mengganti pilihan sebelum dikunci.
aku cuma mencatat tampilan, belum menyebut alasan pergantiannya.
alasan harus diambil dari teks penjelasan kalau tersedia.
iya, tampilan tombol saja tidak memuat motif.
aku menyimpan satu salinan sebelum kunci muncul.
salinan setelah kunci punya waktu yang berbeda.
dua waktu itu tidak akan digabung jadi satu peristiwa.
hasil akhir berada pada bagian paling bawah urutan.
siapa pun bisa membandingkan salinan sesuai waktunya.
oke, batas antara pilihan sementara dan final sudah jelas.
'''),
('pengakuan {a} memakai dua sebutan untuk role yang sama.', '''
buat grup, satu bagian menulis warga biasa dan satu lagi Civilian.
dua istilah itu sama-sama muncul dalam teks asli.
aku akan menyimpan keduanya, bukan menghapus salah satunya.
catatan istilah boleh menjelaskan arti tanpa mengubah kutipan.
iya, yang dibahas tetap satu pengakuan role.
nomor malam tidak disebut pada pengakuan ini.
tidak ada laporan aksi di baris berikutnya juga.
jadi informasi yang tersedia sekarang hanya klaim tersebut.
aku mencatat waktu kirimnya untuk urutan diskusi.
role yang diklaim tetap belum menjadi kepastian publik.
sekarang kita bisa menanggapi isi pengakuannya.
'''),
('pesan {a} tentang koneksi datang setelah chat aktif lagi.', '''
untuk semua, aku mencatat waktunya saat pesan masuk.
status aktif yang terlihat hanya keadaan layar chat.
alasan koneksi berasal dari isi pesan yang dibagikan.
dua jenis informasi itu jangan ditukar tempat.
aku taruh pengamatan layar di samping waktu kirim.
kutipan alasan disimpan dalam bagian isi chat.
iya, tidak perlu kita menambahkan perkiraan durasi putus.
durasi persis memang belum tertulis di sini.
yang bisa dilihat bersama adalah urutan sebelum dan sesudah aktif.
aku masih menyimpan kedua tampilan pada catatan.
baik, urutan teknisnya sudah siap dibahas.
'''),
('laporan {a} menyebut pilihan skill tanpa nama penerimanya.', '''
buat semuanya, di teks hanya ada jenis skill dan malamnya.
nama penerima memang tidak muncul pada kalimat ini.
aku membiarkan kolom nama tetap kosong pada salinan.
jangan isi dengan nama yang kebetulan dibahas di tempat lain.
iya, itu akan menambah informasi yang tidak tertulis.
pesan berikutnya belum memberi nama juga.
aku menandai bagian itu sebagai belum dilaporkan.
jenis skill tetap tercatat sesuai kata aslinya.
nomor malam bisa kita simpan tanpa menebak sasaran.
sekarang batas informasi dalam laporan itu sudah terlihat.
silakan lanjut menilai dari bagian yang memang tersedia.
'''),
('ada kata mungkin pada keterangan hasil {a}.', '''
buat grup, kata mungkin tetap harus ikut saat dikutip.
tanpa kata itu tingkat kepastian tulisannya akan berbeda.
aku menyalin mulai dari awal klausa.
keterangan hasil berada setelah tanda titik dua.
kata mungkin ada di bagian yang sama, bukan pesan terpisah.
iya, aku melihat susunan yang sama di chat lengkap.
salinan singkat sebelumnya belum memuat kata awal itu.
aku akan memakai salinan lengkap untuk diskusi ini.
dua versi salinan tetap bisa ditunjukkan asalnya.
kutipan lengkap tidak menambah kepastian dari pembaca.
baik, isi hasilnya kini bisa dibaca sesuai kalimat asli.
'''),
('pesan {a} tentang perubahan pilihan diawali dengan penjelasan waktu.', '''
bagian awal menyebut sebelum sesi vote dibuka.
buat semua, kita pakai keterangan itu saat membaca sisanya.
aku mencatat waktu yang disebut terpisah dari waktu kirim.
pesan bisa dikirim setelah peristiwa yang diceritakan.
iya, dua waktu itu belum tentu bertepatan.
bagian akhir kalimat membahas rencana berikutnya.
aku memisahkan rencana dari kejadian yang diceritakan.
kata akan masih ikut pada kutipan bagian akhir.
jadi belum perlu ditulis sebagai pilihan yang sudah masuk.
urutan cerita dan rencana sudah tersalin lengkap.
sekarang kita bisa menilai keterangannya tanpa menukar waktu.
'''),
('klaim {a} hanya terlihat sebagian pada ringkasan awal.', '''
aku membuka chat lengkap supaya bisa melihat sisanya.
untuk seluruh grup, ringkasan awal berhenti di tengah kalimat.
bagian lanjutan masih berada dalam pesan yang sama.
aku menyalinnya bersama tanda baca akhir.
ada keterangan nomor malam pada bagian lanjutan itu.
nomor tersebut belum muncul di ringkasan pertama.
iya, kutipan lengkap memuat lebih banyak informasi.
aku akan menandai ringkasan lama sebagai potongan saja.
teks lengkap tetap punya waktu kirim yang sama.
perbedaan panjang salinan tidak berarti ada pesan baru.
baik, kita sudah punya kalimat lengkap untuk dibahas.
'''),
('dalam laporan {a}, kata Guard dan Peek disebut pada dua bagian berbeda.', '''
buat semua, jangan satukan dua jenis skill itu dalam satu kolom.
aku membaca pengantar sebelum masing-masing kata.
bagian pertama berupa pertanyaan, bagian berikutnya berupa pernyataan.
jadi bentuk kalimatnya memang berbeda.
aku mempertahankan tanda tanya pada salinan awal.
tanda titik mengakhiri bagian pernyataan.
iya, batasnya terlihat pada chat lengkap.
jenis kalimat tidak perlu diubah menjadi pengakuan aksi ganda.
aku menulis dua bagian sesuai bentuk aslinya.
belum ada tambahan informasi tentang siapa penerima skill.
sekarang dua bagian tersebut bisa kita baca terpisah.
'''),
('alasan yang ditulis {a} muncul sesudah pertanyaan umum tentang chat.', '''
pertanyaan awal ditujukan ke seluruh grup, bukan satu orang.
buat semua pencatat, sapaan kalian masih terlihat di kalimat itu.
aku salin pertanyaan lengkap di atas jawabannya.
jawaban yang masuk membahas kondisi koneksi.
itu berbeda jenis informasi dari klaim role.
iya, aku tidak menaruhnya pada kolom identitas.
urutan waktu masih bisa kita simpan seperti biasa.
bagian alasan tidak menyebut nomor malam tertentu.
aku biarkan nomor malam kosong pada catatan tersebut.
supaya tidak tercampur dengan laporan aksi yang sedang kita kumpulkan.
oke, konteks pertanyaan umum sudah ikut tercatat.
'''),
('pesan {a} tentang hasil malam memakai tanda garis miring.', '''
aku mau pastikan garis miring itu tetap terlihat di kutipan.
untuk semua, dua kata di sebelahnya belum dijelaskan lebih lanjut.
aku tidak akan memilih salah satu untuk mengganti teks asli.
kalimat berikutnya belum menjelaskan hubungan kedua kata itu.
jadi kutipan perlu mempertahankan bentuknya.
iya, pembaca bisa menilai setelah melihat teks lengkap.
aku menyalin spasi dan tanda bacanya juga.
ringkasan satu kata akan kehilangan bentuk garis miring itu.
lebih baik kita pakai kutipan lengkap pada diskusi ini.
jam kirim masih tercatat pada baris yang sama.
sekarang bagian yang ingin dibahas sudah tampil utuh.
'''),
('aku mencatat {a} menyebut dua waktu kirim yang berbeda.', '''
buat grup, salah satu waktu mengacu pengiriman dan yang lain pembacaan.
dua keterangan itu tertulis pada klausa terpisah.
aku menaruh judul waktu kirim untuk klausa pertama.
klausa kedua tetap memakai judul waktu baca.
iya, jangan dirata-ratakan jadi satu angka.
ada jeda yang disebut, tetapi durasinya tidak ditulis.
aku hanya mencatat bahwa ada jeda dalam ceritanya.
perkiraan panjang jeda belum akan ditambahkan.
urutan klausa sudah cocok dengan salinan lengkap.
semua bisa membandingkan dua waktu itu dari teksnya.
baik, jenis waktu yang dibahas sudah tidak tertukar.
'''),
('laporan {a} menyebut hasil lama sebelum hasil ronde sekarang.', '''
buat semuanya, kita baca penanda waktunya dahulu.
bagian hasil lama diawali kata sebelumnya.
hasil ronde sekarang baru muncul sesudah kata sekarang.
aku pisahkan keduanya dalam catatan waktu.
isi masing-masing tetap dikutip tanpa penyesuaian.
iya, dua hasil tidak boleh digabung menjadi satu kalimat baru.
aku juga mempertahankan nama skill pada setiap bagian.
pesannya sendiri dikirim sekali dalam satu blok.
waktu kirim tunggal tidak membuat dua kejadian itu bersamaan.
urutan cerita sudah cukup jelas untuk disalin.
oke, perbandingan hasil bisa dibaca berdasarkan waktu yang disebut.
'''),
('ada singkatan nomor malam pada chat {a}.', '''
untuk semua yang mencatat, singkatannya terdiri dari huruf dan angka.
aku menyimpan bentuk aslinya dulu tanpa menambahkan kepanjangan.
di pesan berikutnya ada keterangan malam kedua.
keterangan itu bisa ditulis sebagai tambahan terpisah.
iya, jangan mengganti kutipan awal diam-diam.
aku menandai nomor urut kedua pesan.
waktu kirimnya berjarak beberapa baris chat.
tidak ada pergantian fase di antara dua pesan itu.
jadi urutan percakapannya masih berada di sesi diskusi yang sama.
salinan awal dan tambahan sudah terbaca bersama.
baik, penjelasan angka bisa kita bahas dari dua pesan tersebut.
'''),
('klaim {a} disampaikan sebelum pertanyaan tentang hasil skill.', '''
buat grup, urutannya klaim dulu baru sesi tanya hasil.
aku punya salinan kedua bagian percakapan itu.
klaim pertama belum menyebut sasaran maupun nomor malam.
pertanyaan berikutnya baru meminta rincian aksi.
iya, jawaban yang belum ada jangan ditempelkan pada klaim awal.
aku membiarkan bagian rincian tetap kosong sementara.
nama role yang ditulis tetap masuk bagian klaim.
bagian waktu chat bisa tetap diisi dari urutan tampil.
dua kolom itu tidak memerlukan tebakan tentang aksi.
sekarang siapa pun bisa melihat batas informasi saat klaim dikirim.
oke, pembahasan bisa kembali ke isi klaim yang tersedia.
'''),
('teks {a} memakai kata aman setelah menyebut Guard.', '''
buat semuanya, kita perlu tetap menyimpan nama skillnya.
kata aman bisa dibaca berbeda jika jenis skill dihapus.
aku menulis Guard di sebelah kutipan hasil.
tidak ada kata Civilian pada bagian yang sedang disalin.
iya, kita tidak perlu menambahkan nama role sendiri.
bagian waktu hanya menyebut malam yang baru selesai.
aku catat keterangan waktu itu apa adanya.
identitas korban tidak muncul sebagai pengumuman publik di sini.
jadi sumber yang kita punya tetap laporan dalam chat.
seluruh kutipan beserta nama skill sudah tersimpan.
sekarang kita bisa membahas laporan dengan jenis informasinya jelas.
'''),
('pesan {a} soal alasan vote punya tambahan dalam kurung.', '''
aku sedang membaca bagian dalam kurung bersama kalimat utamanya.
untuk grup, tambahan itu menyebut waktu pembacaan chat.
kalimat utama membahas pilihan yang disampaikan sebelumnya.
aku pisahkan isi tambahan tanpa menghapus tandanya.
iya, tanda kurung menunjukkan bagian penjelas dalam teks.
belum tentu tambahan itu adalah peristiwa yang terjadi sesudahnya.
urutan kejadian harus dibaca dari kata waktunya.
aku tetap menyimpan kata sebelum pada bagian dalam kurung.
kalimat di luar kurung juga tidak akan diubah.
sekarang kutipan lengkap bisa dibaca tanpa kehilangan tambahan tersebut.
baik, kita bisa lanjut menilai alasan yang dituliskan.
'''),
('catatan {a} menggunakan kata tadi untuk dua kejadian.', '''
buat semua, dua kata tadi itu ada pada kalimat yang berbeda.
kalimat pertama membicarakan chat, yang kedua membicarakan malam.
aku tidak akan memberi satu waktu yang sama untuk keduanya.
keterangan peristiwa tetap harus ikut saat dikutip.
iya, kata waktu saja belum cukup tanpa isi kalimat.
aku menambahkan pemisah antarkalimat di salinan.
nomor malam yang eksplisit hanya ada pada bagian kedua.
bagian chat belum memiliki angka menit.
jadi kolom waktu chat tetap berupa keterangan yang tertulis.
kedua kalimat sudah tersalin dengan konteksnya masing-masing.
oke, sekarang penggunaan kata tadi bisa dibaca lebih jelas.
'''),
('hasil yang ditulis {a} ditempatkan setelah pengantar klaim Stalker.', '''
buat grup, kita salin pengantar dan hasilnya dalam urutan itu.
pengantar menyebut role yang diakui, bukan pengumuman sistem.
bagian sesudah titik dua menyampaikan hasil yang dilaporkan.
aku menyimpan tanda titik dua agar batasnya terlihat.
nomor malam disebut pada akhir pesan.
angka tersebut tidak perlu dipindah ke pengantar role.
iya, posisi aslinya tetap bisa dibaca pada kutipan.
aku membuat catatan terpisah tentang waktu laporan masuk.
waktu masuk pesan bukan otomatis waktu skill dipakai.
dua informasi waktu itu sekarang berada di tempat berbeda.
baik, klaim dan laporan hasil sudah siap dibahas bersama.
'''),
('penjelasan {a} mengenai jeda chat memakai perkiraan durasi.', '''
untuk semua, ada kata sekitar sebelum angka durasinya.
aku akan mempertahankan kata itu pada kutipan.
tanpa sekitar, angka tersebut terlihat seperti ukuran pasti.
catatan tampilan kita sendiri tidak memuat detik lengkap.
iya, yang tersedia hanya urutan pesan masuk.
aku pisahkan perkiraan dalam cerita dari waktu yang terlihat.
dua bagian ini tidak boleh digabung menjadi pengukuran baru.
angka asli tetap disimpan sebagai bagian dari penjelasan.
urutan chat juga masih utuh di salinan grup.
sekarang batas antara perkiraan dan pengamatan sudah jelas.
oke, kita bisa menilai penjelasannya sesuai informasi yang ada.
'''),
('pesan {a} tentang pilihan akhir dikirim saat diskusi hampir tutup.', '''
buat semua, kata akhir di sini ada pada isi pesan.
itu tidak otomatis berarti tombol pilihan sudah terkunci.
aku sedang membandingkan waktu pesan dengan perubahan tampilan.
pengumuman kunci vote baru datang setelahnya.
iya, ada jeda antara dua peristiwa yang terlihat.
aku tidak punya durasi tepat untuk jeda tersebut.
catatan akan memakai urutan saja pada bagian ini.
isi pilihan tetap disalin sesuai teks, tanpa alasan tambahan.
kalau ada alasan tertulis, tempatnya di bagian pesan penjelasan.
sekarang pernyataan pilihan dan status layar sudah terpisah.
baik, kita bisa kembali ke isi keputusan yang dikirim tadi.
'''),
('laporan {a} tentang malam tadi tersimpan sebagai satu pesan panjang.', '''
aku membaginya per kalimat supaya semua bisa membaca runtut.
untuk grup, pembagian ini cuma tampilan catatan, bukan pesan baru.
kalimat pertama berisi klaim role.
kalimat berikutnya menyebut jenis skill yang dilaporkan.
bagian akhir menambahkan waktu kejadian.
iya, urutan itu tetap sama dengan paragraf aslinya.
aku belum menghapus kata penghubung apa pun.
kalau dibaca per bagian, kaitannya tetap bisa dilihat.
waktu kirim seluruh paragraf cuma satu.
nomor malam di isi pesan tetap dicatat terpisah dari waktu kirim.
oke, paragraf utuh dan versi per kalimat tersedia untuk dibahas.
'''),
]

assert len(EXTRA)==40
assert all(len(body.strip().splitlines())==11 for _,body in EXTRA)
