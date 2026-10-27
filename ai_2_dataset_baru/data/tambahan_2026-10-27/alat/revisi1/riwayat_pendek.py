def lines(text):return text.strip().splitlines()

PAIR = lines('''
{a} sama {b} baru jawab setelah sama-sama diam sebentar.
nih, {b} dan {a} dua-duanya lagi cerita soal malam kedua.
{a} juga {b} sempat pindah pilihan sebelum vote dikunci.
{b} dan {a} sama-sama ngaku Spy di chat tadi.
yang barusan nanya hasil malam itu {a} sama {b}.
{b} serta {a} belum nulis hasil Peek lengkap, baru pengantarnya.
{a} dan {b} masing-masing bilang sudah pakai skill malam itu.
dua jawaban yang belum selesai itu dari {b} dan {a}.
{a} sama {b} kirim klaim pas diskusi baru kebuka.
{b} juga {a} sama-sama menyebut Stalker sebagai role-nya.
gw baca {a} dan {b} cerita soal jeda chat dengan urutan yang sama.
{b} dan {a} belum menyebut kapan pindah vote, sih.
{a} juga {b} baru ngomong soal sinyal di ronde ini.
yang belum mengaku role ada {b} sama {a}, keduanya masih ngetik.
{a} dan {b} masing-masing mengubah angka malam yang ditulis.
{b} serta {a} sama-sama minta hasil skill dibahas lebih dulu.
{a} sama {b} menulis Civilian, jawabannya pendek-pendek.
{b} dan {a} baru selesai menjelaskan kenapa belum memilih.
{a} juga {b} berhenti mengetik pas sesi vote dimulai.
dua orang yang masih cerita soal malam tadi itu {b} dan {a}.
{a} serta {b} sama-sama menyebut chat sempat terkunci.
{b} sama {a} belum menulis nama role lengkap di hasilnya.
yang mau bahas dua klaim ini, nih, dari {a} dan {b}.
{b} juga {a} ganti keterangan soal malam pertama.
{a} dan {b} masing-masing minta vote diselesaikan sekarang.
''')

# 50 untuk ambiguous, 25 untuk plural_reference; semuanya merujuk tepat dua orang.
PAIR_REPLY = lines('''
dua orang itu lagi dibahas bareng ya, belum ke salah satunya.
gw masih baca jawaban keduanya dari atas.
cerita mereka berdua masuk pada ronde yang sama.
kalau soal dua klaim itu, aku belum kasih kesimpulan.
dua nama tadi masih sama-sama ditanya soal malamnya.
aku pengin dengar urutan aksi keduanya dulu dong.
pesan mereka berdua belum selesai kubaca sih.
keduanya menyebut waktu yang sama dalam cerita itu.
aku masih menunggu tambahan dari dua orang tadi.
yang dibahas tetap dua pemain itu kok, belum pindah ke orang lain.
dua klaim tadi belum kita urutkan satu-satu.
gw buka lagi chat mereka berdua sebelum menjawab.
alasan keduanya memang masuk berdekatan di layar sini.
aku belum tahu kedua orang itu mau nambah penjelasan atau nggak.
nih, dua pesan mereka masih kelihatan di atas.
kalau keduanya punya tambahan, masih ada waktu ngomong.
gw denger dua cerita itu dulu sampai selesai.
dua orang tersebut sekarang sama-sama belum nulis lagi.
aku lagi membaca bagian waktu pada jawaban keduanya.
mereka berdua belum menyebut detik persisnya sih.
giliran dua orang itu masih belum selesai, ya.
aku belum misahin pembahasan mereka jadi dua topik.
keduanya masih ngomongin fase malam, bukan hasil vote.
gw coba pahami dua jawaban itu sebelum ikut komentar.
chat kedua orang tadi sama-sama masih muncul di layar.
yang satu belum dipilih dari keduanya untuk ditanya lebih dulu.
aku melihat kedua klaim itu, tapi belum menentukan sikap.
dua orangnya masih dibicarakan sekaligus, nih.
gw pengin tahu apakah keduanya merujuk malam pertama.
pesan dari dua pemain itu belum tenggelam, masih bisa dibaca kok.
aku ikuti pembicaraan keduanya sampai bagian akhir.
dua cerita tadi nggak akan kutukar urutannya saat dibaca.
masih soal mereka berdua, kita belum bahas peserta lain.
aku belum menanggapi salah satu dari dua klaim itu.
angka malam pada pesan keduanya sudah kelihatan sekarang.
gw lagi nunggu mereka berdua selesai mengetik dong.
dua pengakuan tadi aku baca apa adanya dulu.
soal kedua pemain itu, informasi yang masuk belum bertambah.
keduanya sempat menyebut jenis skill pada pesan awal.
aku belum memilih satu cerita dari mereka untuk dibahas dulu.
nih, dua orang itu belum menjelaskan bagian akhirnya.
aku lihat jawaban keduanya masih sebatas yang tadi.
yang satu dan yang satunya lagi sama-sama sedang ditanya.
gw masih membandingkan waktu pada dua pesan tersebut.
kalau bicara kedua orang itu, bagian role-nya sudah terbaca.
aku mau membaca ulang ucapan mereka, belum bikin keputusan.
dua nama yang dibahas itu belum berubah dari tadi sih.
keduanya punya pesan lanjutan yang masuk hampir barengan.
aku belum mengakhiri pembahasan salah satu dari mereka.
cerita dua pemain itu masih jadi topik kita sekarang.
gw baca dulu klaim mereka berdua, baru kasih pendapat.
dua orang tadi baru selesai ngomong, aku masih menyimak.
sekarang aku lagi lihat hasil yang disebut keduanya.
aku mau pahami alasan mereka, bukan sekadar lihat nama role.
pesan keduanya masih bisa kubuka dari layar ini.
nih, aku belum selesai baca bagian malam mereka.
keduanya punya penjelasan yang masuk setelah pertanyaan grup.
aku belum menanggapi dua klaim itu karena masih membacanya.
gw pengin tahu urutan waktu mereka berdua secara lengkap.
dua jawaban tadi aku ikuti dari awal sampai titik terakhir.
aku menunggu mereka selesai mengirim semua bagian pesan.
yang dua itu baru saja menambah keterangan soal waktu.
gw masih menyimak apa yang keduanya sampaikan.
kedua pemain itu masih jadi bahasan, aku belum pindah topik.
aku lihat nomor malam pada hasil mereka berdua.
dua klaim yang mereka tulis sama-sama masih ada di atas.
sebelum memberi tanggapan, aku baca pesan keduanya sekali lagi.
gw belum jawab mereka berdua, masih lihat isi klaimnya nih.
keduanya sekarang sudah menyebut waktu penggunaan skill.
aku sedang memahami cerita mereka tanpa memotong bagian awal.
dua pemain tadi punya jawaban yang datang berurutan.
aku ingin membaca hasil dari keduanya sampai tuntas dong.
yang mereka sampaikan sudah masuk, aku baru mulai bacanya.
gw lihat pertanyaan ke dua orang itu masih soal malam yang sama.
aku sedang mengikuti penjelasan kedua pemain tadi kok.
''')

# Netral tanpa sasaran: percakapan untuk grup, tidak menyapa individu.
GROUP = lines('''
semua yang punya info tambahan boleh ngomong sekarang.
gw masih nyimak obrolan ronde ini, lanjut aja.
kalau ada pesan sambungan, kirim sekalian dong.
waktu diskusinya masih ada buat seluruh pemain.
aku belum bikin keputusan, masih baca chat yang masuk.
yang udah selesai ngetik boleh kirim, nggak perlu tunggu giliran panjang.
grupnya masih terbuka kok, semua bisa tanggapi.
aku sudah sampai pesan terakhir sekarang nih.
kalau mau bahas hasil skill, sebut malamnya juga ya semuanya.
gw belum pindah ke menu vote, masih di chat.
semuanya boleh kasih pendapat, asal kalimatnya selesai dulu.
aku lagi ikutin urutan obrolan dari pembukaan.
hasil malam bisa dibahas setelah pengantar klaimnya.
pesan yang tadi masuk masih terbaca di layar grup.
ayo lanjut, masih ada beberapa hal yang ingin kudengar.
gw sekarang baca sambil nunggu hasil yang belum ditulis.
buat semua, kirim satu-satu aja kalau pesannya kepanjangan.
aku sudah lihat bagian awal obrolannya kok.
kalau ada keterangan waktu, jangan dicampur dengan jam kirim.
diskusinya belum berakhir, lanjut ngomong aja nih.
aku menyimak dulu sebelum ikut menentukan vote.
siapa pun yang belum selesai cerita masih bisa lanjut.
gw pengin dengar isi lengkapnya, jangan cuma nama role.
semua masih bisa baca pesan sebelumnya dari chat ini.
aku lagi di bagian akhir percakapan sekarang.
buat grup, pertanyaan berikutnya boleh sekalian dikirim.
kita masih bisa ngobrol sebentar sebelum memilih.
kalau bahas malam pertama, sebut dari awal dong.
gw sih masih menunggu pendapat yang belum masuk.
aku belum menutup layar chat, silakan diteruskan.
semua boleh menambahkan info yang memang diketahui.
pesan baru udah kelihatan di bawah sekarang nih.
kalau ada jawaban lanjutan, biarkan selesai dulu baru dibaca bareng.
aku sudah membaca pertanyaan grup sebelumnya.
lanjut ke hasil malamnya aja, semuanya masih di sini.
gw ingin dengar alasan memilih sebelum tombol vote muncul.
obrolan soal role belum selesai, jadi terusin dulu.
aku masih bisa melihat pesan dari pembukaan ronde.
buat semuanya, bagian nomor malam jangan lupa disebut.
yang mau menjawab boleh pakai pesan pendek juga kok.
aku ngikutin obrolan ini sampai semua selesai.
kalau ada info lain, tulis di chat sebelum fasenya ganti.
gw baru sampai akhir pesan yang panjang itu nih.
semua bisa membaca klaim yang sudah dikirim di atas.
aku pengin bahas satu malam dulu baru lanjut berikutnya.
kita masih ada kesempatan bertanya sebelum memilih.
kalau jawabannya dua bagian, kasih sambungannya juga dong.
aku lagi melihat urutan hasil yang dilaporkan di grup.
semuanya boleh menanggapi setelah kalimatnya lengkap.
gw masih membuka obrolan ini, belum beralih layar.
aku baca pelan dulu, banyak pesan masuk bersamaan.
buat semua, bahas jenis skill dan hasilnya sekalian ya.
gw pengin tahu alasan di balik masing-masing pilihan.
urutan chat dari awal masih bisa dilihat kok.
kalau mau bertanya, sekarang masih kebagian waktu.
aku belum memutuskan apa pun, dengerin dulu aja.
kita bisa lanjut dari bagian yang terakhir dikirim.
semuanya, jangan campur hasil ronde lama dengan yang baru dong.
gw sudah selesai membaca pengantarnya sekarang.
pesan berikut boleh masuk nih, grupnya masih aktif.
aku ngikutin penjelasan yang ada sebelum ikut bicara.
kalau ada alasan tambahan, sampaikan di sini saja.
buat grup, kita pakai nomor malam yang sama waktu ngobrol.
gw masih bisa scroll ke percakapan sebelumnya.
semua yang belum jawab pertanyaan boleh menyusul.
aku belum lihat pengumuman vote terkunci di layar.
boleh lanjut, obrolan hasil malam masih belum selesai.
yang sedang mengetik nggak perlu memotong kalimat di tengah.
gw baca dari pesan pertama ronde ini sih.
kalau mau menjelaskan urutannya, mulai sebelum fase malam saja.
aku sedang menyimak tanpa ikut memilih dulu.
untuk semuanya, sambungan pesan bisa dikirim setelah ini.
grup masih ada waktu menanyakan bagian yang belum jelas.
aku sudah membuka seluruh chat, bukan cuma notifikasi.
ayo bahas isi klaimnya sebelum menu pemilihan muncul.
gw menunggu penjelasan selesai baru komentar.
semua bisa lihat nama skill yang ditulis dalam pesan awal.
kalau satu baris kurang, kirim lanjutannya di bawah dong.
aku baru baca bagian nomor malamnya nih.
kita belum selesai mengobrol soal kejadian sebelum vote.
buat grup, hasil yang berbeda malam dibahas bergantian aja.
gw masih menyimak kalimat terakhir yang masuk.
yang mau menambahkan sesuatu, sekarang boleh ketik.
aku ingin urutan kejadian dijelaskan dari awal sampai akhir.
pesan-pesan sebelumnya masih kelihatan dari sini kok.
kalau ada pertanyaan umum, kirim ke grup sekalian.
aku belum beranjak dari layar diskusi ini.
buat semua, hasil yang cuma sebagian bisa dilengkapi dulu.
gw pengin dengar dua sisi penjelasan sebelum putuskan apa pun.
sekarang lanjut saja, timer belum menunjukkan akhir diskusi.
aku sedang membaca isi chat, bukan melihat hitungan suara.
semuanya boleh memberi tanggapan dengan alasan yang jelas.
kalau mau bahas malam lain, bilang nomornya di awal ya.
gw udah sampai pesan paling bawah nih, lanjutkan.
bagian pertanyaan grup masih bisa dijawab sekarang.
aku belum melihat seluruh laporan, jadi dengarkan dulu.
silakan kirim penjelasan berikutnya, kolom ketiknya masih ada.
buat grup, baca kalimat lengkap sebelum menanggapi dong.
gw masih mengikuti apa yang dibicarakan sejak tadi.
aku ingin lihat isi hasilnya dulu sebelum arah vote dibahas.
yang belum cerita soal dirinya boleh lanjut sekarang.
semua boleh ambil giliran, aku masih menyimak.
kalau ada yang mau menyampaikan role, silakan di chat.
gw belum selesai membaca percakapan yang masuk barengan.
aku masih ada di layar diskusi kok, lanjut aja.
buat semuanya, tidak perlu satu pesan panjang kalau bisa dicicil.
giliran ngomongnya masih terbuka untuk seluruh grup.
nih, kolom ketik belum berganti jadi menu pilih.
aku menunggu penjelasan berikut sambil baca pesan awal.
siapa pun yang belum menyampaikan alasan masih bisa ngomong.
gw dengarkan dulu, keputusan bisa setelah ceritanya selesai.
buat grup, yang ingin menjawab boleh mulai dari role-nya.
aku sudah melihat pengumuman fase, sekarang masih diskusi.
kalau ada jawaban yang belum selesai, lanjutkan di bawah dong.
semua bisa menambahkan bagian yang belum sempat disampaikan.
gw masih membuka chat dari awal sesi ini.
yang ingin ngomong setelah ini nggak perlu menunggu lama.
aku baca dulu pesan masuk sebelum kasih tanggapan.
buat semua, ngobrolnya bisa diteruskan sampai timer berhenti.
sekarang yang belum menjelaskan punya waktu sebentar lagi.
aku belum menekan pilihan apa pun, masih dengar obrolan.
grupnya masih bisa menerima pesan baru nih.
kalau ada yang baru selesai baca, boleh menanggapi sekarang.
gw pengin semua sempat menyampaikan pendapatnya.
yang mau menjelaskan jeda chat atau aksi bisa lanjut.
aku sedang mengikuti pembicaraan sambil menunggu fase berikut.
buat seluruh pemain, masih ada kesempatan mengirim jawaban.
kalau penjelasannya kepotong, sambung saja dari kata terakhir.
gw masih menyimak sih, belum punya keputusan akhir.
aku membaca pesan yang di atas sambil menunggu yang baru.
semua yang belum ngomong bisa masuk setelah ini dong.
di layar sini obrolannya masih terus jalan.
aku belum meninggalkan diskusi, jadi lanjutkan saja.
buat grup, kita masih bisa bertanya satu putaran lagi.
kalau ada hal yang ingin dijelaskan tentang diri sendiri, sekarang boleh.
gw sudah membaca pesan sebelumnya sampai tuntas kok.
yang belum sempat kirim jawaban bisa pakai sisa waktu ini.
aku menunggu keterangan berikutnya dari grup.
semua masih bisa membuka pesan lama kalau perlu baca ulang.
nih, belum ada tombol kunci pada fase chat sekarang.
aku mendengarkan dulu sebelum mengarahkan pilihan.
buat semuanya, silakan lanjut ke penjelasan yang tertunda.
yang sedang membaca bisa menanggapi setelah selesai.
gw masih ingin tahu urutan kejadian sebelum vote dimulai.
aku menyimak di sini, tidak sedang membuka menu lain.
kalau ada yang baru mau klaim, tulis sekarang sebelum fase berganti.
semua boleh menjawab dengan kata-kata sendiri aja.
aku sudah sampai akhir obrolan, siap membaca pesan lanjutannya.
buat grup, masih ada waktu untuk satu penjelasan pendek.
gw belum menutup diskusi ini, lanjut dong yang belum selesai.
''')

TIMERS=lines('''
eh semuanya, empat puluh detik lagi sebelum vote.
di layar gw masih semenit buat ngobrol nih.
timer diskusi tinggal tiga puluh, grupnya belum tutup.
buat semua, hitungannya baru lewat separuh.
masih lima puluh detik kok sebelum fase memilih.
pengingat aja, dua puluh detik lagi chatnya selesai.
nih, timer udah masuk angka belasan.
semuanya, masih ada satu menit lebih sedikit.
kolom diskusi masih terbuka, hitungannya tinggal dua puluh lima.
di pojok layar tinggal empat puluh lima detik.
waktunya belum habis, semua masih bisa kirim sebentar lagi.
grup, tiga puluh lima detik lagi pindah fase.
aku lihat timer ngobrol baru turun ke lima puluh.
sebentar, jam di game menunjukkan sisa lima belas detik.
semua, jangan lupa sebentar lagi masuk sesi vote.
masih ada setengah menit buat percakapan terakhir nih.
layar belum ganti, diskusinya tersisa sekitar empat puluh detik.
timerku sudah dua puluh delapan, buat info semuanya.
sesi ngobrol masih jalan kok, bukan vote sekarang.
nih, hitungan menuju pemilihan mulai kedip.
semua masih punya tiga perempat menit untuk menjawab.
angka waktunya turun ke dua puluh, tinggal sebentar.
buat grup, baru lima belas detik sejak diskusi dimulai.
aku lihat tulisan sisa satu menit di atas chat.
pengumuman ke semua, ronde ini masih di fase diskusi.
masih empat puluh dua detik di timer sini nih.
eh grup, sesi memilih belum terbuka, masih ngobrol.
hitungan diskusi udah tiga puluh dua sekarang.
buat seluruh pemain, tinggal setengah menit lebih dikit.
di layar gw enam puluh detik sebelum chat berakhir.
timer ngobrol masih panjang sih, sekitar lima puluh lima.
nih, baru muncul pengingat sepuluh detik terakhir.
semuanya, tombol vote belum aktif sampai timer ini habis.
sisa waktu grup tinggal dua puluh dua detik.
aku lihat penghitung fase masih di empat puluhan.
buat semua yang belum sadar, hitungannya udah mau habis.
masih ada tiga puluh delapan detik buat mengetik.
eh, pengingat waktu muncul, diskusi tinggal belasan detik.
nih waktunya lima puluh delapan, masih cukup buat grup.
fase ini belum pindah kok, timer diskusi masih bergerak.
semua, waktu untuk ngobrol tersisa dua puluh enam.
jam di atas kolom chat menunjukkan sisa empat puluh delapan.
aku cuma ngingetin grup, sekitar semenit lagi kita memilih.
angka sebelas udah muncul di timer diskusi.
buat semuanya, seperempat menit lagi layar berubah.
masih tiga puluh satu detik menurut tampilan game.
nih, timer untuk fase ngobrol turun ke tujuh belas.
semua yang masih mengetik punya sisa waktu sekitar dua puluh detik.
diskusi belum dikunci, di sini hitungannya empat puluh sembilan.
aku lihat pengumuman fase vote akan mulai sebentar lagi.
grup, waktu ngobrol masih sekitar satu menit kok.
pengingat untuk semua, sisa diskusi tiga puluh tiga detik.
di timer sini cuma sembilan belas detik lagi.
nih, kolom chat akan tutup setelah hitungan terakhir itu.
semuanya, fase malam berikutnya belum mulai, kita masih diskusi.
aku lihat sisa dua puluh tujuh pada jam game.
masih ada lima puluh satu detik sebelum giliran vote.
buat grup, hitungan pemilihan belum dimulai sama sekali.
eh, waktu ngobrol tinggal empat belas detik sekarang.
nih, fase chat masih berjalan selama sekitar setengah menit.
di pojok atas ada angka empat puluh enam untuk sisa waktu.
semua, masih cukup untuk pesan pendek sebelum timer habis.
layarnya belum berubah, sisa waktu diskusi dua puluh sembilan.
aku ngingetin saja, lima detik terakhir sudah mau mulai.
buat grup, sisa tiga puluh tujuh detik sebelum memilih.
timer diskusi baru menunjukkan angka lima puluh tiga nih.
semuanya, pengumuman sepuluh detik lagi sudah terlihat.
aku masih lihat empat puluh satu pada jam diskusi.
fase ngobrol masih aktif kok, ada dua puluh empat detik.
nih, hitungan di layar tinggal dua belas sebelum chat ditutup.
buat seluruh grup, waktu memilih akan datang setelah ini.
masih tiga puluh sembilan detik di sesi diskusi kita.
aku baru lihat timer lewat dari semenit ke lima puluhan.
semuanya, tersisa delapan belas detik buat kalimat terakhir.
pengingat singkat, kolom diskusi masih buka sekitar empat puluh detik.
''')

ROLE = lines('''
gw Spy, nanti sekalian cerita kapan pakai Guard.
aku ngaku Stalker dulu ya, hasil Peek habis ini.
role-ku Civilian, cuma itu info dari aku sekarang.
aku pakai Guard malam kedua, bukan sedang bahas malam pertama.
gw mau buka role Stalker di sini dulu nih.
aku Civilian sih, sekarang giliran buka role kan?
aku mengaku Spy pada ronde ini, lanjut setelah ini ya.
gw Stalker dan sudah pernah Peek sejak permainan mulai.
aku bilang Civilian dari sekarang supaya nggak perlu tanya role lagi.
aku menggunakan Guard saat fase malam yang barusan lewat.
gw nulis klaim Stalker dulu sebelum bahas hasil skill.
aku mau menyebut role-ku Spy, itu pengakuanku sekarang.
gw Civilian, tadi memang belum ikut giliran klaim.
aku udah kirim klaim role dan waktu aksiku di chat tadi.
gw baru selesai menjelaskan urutan kejadian malam dari versiku.
aku sudah menulis role yang kuklaim beserta malamnya.
gw menunggu tanggapan setelah jelasin pilihan vote tadi.
aku selesai cerita soal aksi, sekarang boleh dibahas.
gw barusan nulis alasan pindah pilihan sebelum vote dikunci.
aku sudah menyampaikan klaim lengkap, bukan baru nama skillnya.
gw selesai mengirim penjelasan waktu chat itu.
aku sudah jawab pertanyaan soal role di pesan atas.
gw baru habis menjelaskan kenapa memilih di akhir hitungan.
aku menyebut waktu aksiku pada bagian akhir pesan tadi.
gw sudah kasih cerita dari sebelum malam sampai chat dibuka.
aku selesai mengirim hasil dan pengantar role sekaligus.
gw sudah menuliskan alasan yang ingin dibahas di ronde ini.
aku baru mengirim pesan tentang jeda waktu diskusi tadi.
gw mengaku role itu di atas, lalu menjelaskan urutan malamnya.
aku sudah menjawab soal pilihan yang sempat berganti.
gw baru selesai cerita tentang tampilan saat fase berubah.
aku sudah menjelaskan waktunya, tinggal dengar pendapat grup.
gw telah mengirim jawaban lengkap buat pembahasan malam ini.
aku selesai menulis versi ceritaku tentang hasil skill.
gw sudah menyampaikan klaim, pesan berikutnya soal malam yang sama.
aku baru kirim cerita soal kapan hasil itu terlihat.
gw sudah menuliskan penjelasan sampai bagian terakhir.
aku menyampaikan role dan hasil yang mau kubahas sekarang.
gw mau cerita kapan skill dipakai setelah menyebut role.
aku sedang menyiapkan jawaban tentang jenis aksi malam.
gw udah nulis klaim dan siap bahas waktu penggunaan skill.
aku mau menjelaskan hasil Peek tanpa memotong kalimatnya.
gw sedang membuka obrolan soal role pada ronde ini.
aku selesai mengetik laporan waktu aksiku semalam.
gw baru saja menjelaskan keadaan chat setelah malam selesai.
aku sudah mengirim klaim role untuk dibicarakan bersama.
''')

REQUEST = lines('''
{s}, menurutmu gimana klaim role-ku tadi?
gw mau denger pendapatmu soal alibiku, {s}.
{s}, boleh tanggapi ceritaku tentang malam itu dong?
gimana penilaianmu soal klaimku, {s}, kalau udah baca?
{s}, aku masih nunggu pendapatmu tentang urutan aksiku.
gw ingin kamu kasih tanggapan soal alibiku, {s}.
{s}, bisa bilang pendapatmu tentang role yang kuklaim?
menurutmu cerita malamku tadi gimana sih, {s}?
{s}, tolong baca penjelasanku dan kasih pendapat ya.
aku ingin dengar dari kamu soal klaimku, {s}.
{s}, gimana hasil penilaianmu kalau lihat ceritaku tadi?
gw minta komentarmu soal alibi yang kusampaikan, {s}.
{s}, setelah baca urutannya, kamu menilainya gimana?
aku nanya pendapat kamu soal role-ku nih, {s}.
{s}, bisa tanggapi penjelasan waktu aksiku sekarang?
gw menunggu kamu menilai klaim yang kutulis, {s}.
{s}, bagaimana menurutmu alasan jeda chatku tadi?
aku pengin pendapatmu tentang pengakuan role ini, {s}.
{s}, coba baca penjelasanku lalu kasih penilaian dong.
gw nanya ke kamu soal klaimku, {s}, bukan ke grup dulu.
{s}, menurutmu alibi yang baru kusampaikan itu gimana?
aku ingin tanggapan dari kamu soal role tadi, {s}.
{s}, boleh beri pendapat setelah lihat penjelasan lengkapku?
gw menunggu komentar kamu tentang klaim malam ini, {s}.
{s}, kamu menilai cerita aksiku dari awal tadi bagaimana?
''')
REPLY=lines('''
aku baca penjelasanmu sampai selesai dulu ya.
gw mau lihat urutan ceritamu sebelum menilai.
aku lagi membaca jawabanmu dari pesan pertama kok.
gw perhatikan dulu waktu yang kamu sebut tadi.
aku belum selesai baca klaimmu, sebentar ya.
gw lagi lihat bagian hasil dalam penjelasanmu.
aku ingin baca alibimu utuh sebelum kasih pendapat sih.
gw buka lagi pesanmu yang menjelaskan malam kedua.
aku masih menyimak bagian akhir ceritamu nih.
gw membaca klaimmu dulu, baru bisa menanggapi.
aku ingin lihat semua yang kamu tulis soal aksi itu.
gw lagi mengikuti urutan penjelasanmu dari atas.
aku baca sampai akhir dulu untuk menjawab pertanyaanmu.
''')
WAIT=lines('''
{s}, aku masih nunggu pendapatmu soal klaim tadi.
gw belum dapat tanggapanmu tentang alibiku, {s}.
{s}, kalau sudah selesai baca, bilang penilaianmu ya.
aku menunggu jawabanmu soal role yang kuklaim, {s}.
{s}, komentarmu tentang penjelasanku masih kutunggu kok.
gw belum dengar pendapat kamu soal cerita itu, {s}.
{s}, boleh lanjut tanggapi klaimku setelah selingan waktu tadi.
aku masih bertanya ke kamu soal alibiku nih, {s}.
{s}, kamu sudah punya penilaian tentang klaimku belum?
gw nunggu kamu menanggapi penjelasan awal tadi, {s}.
{s}, sekarang bisa kasih pendapat soal urutan aksiku?
aku masih ingin dengar tanggapanmu tentang role-ku, {s}.
''')

TIME_REPLY=lines('''
iya, di sini juga masih fase diskusi, lanjut aja semuanya.
gw sudah lihat jamnya, obrolannya boleh diterusin.
oke, pengingatnya terbaca di grup, belum perlu pindah layar.
di tempatku hitungannya jalan terus kok, lanjut ngobrol.
buat semua, timer masih sesuai, kita bisa kembali ke bahasan tadi.
aku udah lihat sisa waktunya, silakan teruskan percakapannya.
iya, layar belum ganti fase di sini juga.
gw melihat angka waktunya sekarang, lanjut aja sebelum habis.
oke nih, pengumuman waktu sudah masuk, kembali ke obrolannya.
semua masih bisa mengetik selama hitungan itu berjalan.
aku sudah melihat timernya, grup masih ada waktu sedikit.
iya, sesi memilih belum mulai di layar sini kok.
gw udah perhatikan hitungan di atas, ngobrolnya bisa lanjut.
oke, pengingat fase terbaca, aku kembali membaca chat.
di sini waktu diskusinya juga belum selesai semuanya.
aku lihat angka yang sama sekarang, lanjut ke bahasan awal.
iya nih, kolom ketik masih aktif buat grup.
gw sudah tahu sisa detiknya, silakan sambung percakapan tadi.
oke, belum ada layar hasil vote, kita masih bisa ngobrol.
jamnya sudah kulihat, kembali ke pembicaraan sebelumnya dong.
aku juga melihat timer masih berjalan tanpa berganti fase.
iya, pengingat untuk grupnya terbaca dengan jelas.
di layar sini masih ada kesempatan mengirim pesan juga.
oke kok, waktunya belum habis, lanjutkan saja obrolannya.
gw udah baca pengumumannya, sekarang kembali ke topik sebelum timer.
''')

assert len(PAIR)==25
assert len(PAIR_REPLY)==75,len(PAIR_REPLY)
assert len(GROUP)==150,len(GROUP)
assert len(TIMERS)==75,len(TIMERS)
assert len(ROLE)==46,len(ROLE)
assert len(REQUEST)==25 and len(REPLY)==13 and len(WAIT)==12
assert len(TIME_REPLY)==25
