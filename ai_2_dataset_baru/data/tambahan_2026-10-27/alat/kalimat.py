"""Kalimat utama ditulis satu per satu oleh Codex; placeholder hanya nama roster.
Tidak ada permutasi sinonim untuk memperbanyak pesan utama.
Urutan d/o/n mengikuti labels_for; w berarti bantahan sumber yang membela diri.
"""
BANK = {}
BANK['ambiguous'] = '''
d|dia belum pantas dicoret dari warga, diam sebentar bukan bukti jadi Hitman.
o|aku curiga dia sengaja mengulur pembahasan sampai kesempatan vote habis.
d|jangan arahkan vote ke dia dulu; keterlambatan jawabnya masih bisa dijelaskan.
o|gerak-geriknya bikin ragu, dia seperti sudah tahu siapa yang bakal disandera.
d|menurutku dia bersih. Klaimnya masih nyambung sama urutan kejadian.
o|dia yang perlu kita tekan, ceritanya mendadak ganti setelah hasil Peek keluar.
d|belum tentu dia bohong hanya karena lupa menulis nomor ronde.
o|kalau harus pilih sekarang, aku vote dia karena alasan pindah pilihannya janggal.
d|aku tetap bela dia; mengulang pertanyaan bukan berarti sedang mengalihkan isu.
o|dia kelihatan sedang menyiapkan alibi, bukan benar-benar membantu diskusi.
d|kasih dia ruang menjawab, tuduhan Hitman itu belum punya pegangan.
o|jangan percaya dia mentah-mentah, ada bagian klaimnya yang jelas ngarang.
d|diamnya tadi bukan alasan untuk menuduh dia, bisa saja kena Gag Order.
o|dia terus mendorong orang lain membuka role, motifnya mencurigakan buatku.
d|buatku dia bukan pelaku; alasan soal chat tertahan masih masuk akal.
o|aku nggak beli pembelaannya. Dia terlalu cepat tahu arah hasil malam ini.
d|tolong lepas dulu kecurigaan ke dia, satu jawaban pendek tidak membuktikan apa-apa.
o|dia pantas masuk kandidat vote, perubahan ceritanya terlalu besar untuk salah ketik.
d|hasil pengecekanku justru membersihkan dia, jadi stop dorong eksekusinya.
o|ucapannya soal Guard palsu, aku makin yakin dia Hitman.
d|aku percaya dia warga. Tadi jawabannya tidak bertabrakan dengan catatan malam.
o|yang bikin aku waspada itu dia, selalu mengajak pindah topik pas ditanya alasan vote.
d|kita jangan menghukum dia karena pesannya terpotong; itu bukan pengakuan bersalah.
o|dia sedang menutupi pelaku menurutku, semua sanggahannya cuma memutar perhatian.
d|bagiku tuduhan ke dia gugur setelah penjelasan urutan chat tadi.
o|lebih baik eksekusi dia, klaimnya tidak cocok dengan aksi yang dia ceritakan sendiri.
d|nggak, dia aman kok. Aku dapat hasil Peek yang menyebut Civilian.
o|aku menilai dia berbohong soal kapan bisa bicara lagi; waktunya tidak cocok.
d|bukan dia yang layak dicurigai, jeda mengetiknya masih normal.
o|caranya ikut arus vote bikin dia kelihatan seperti Hitman yang cari aman.
d|aku nggak setuju dia disudutkan cuma karena belum mau buka role.
o|dia pasti menyembunyikan sesuatu, jawaban tentang aksinya muter terus.
d|perbedaan ejaan itu kecil banget, jangan jadikan dia tersangka dari situ.
o|sekarang fokus curigai dia; pengakuannya soal Peek saling bertentangan.
d|dia tetap kubela, status chat yang terkunci tidak bisa dipakai sebagai bukti pelaku.
o|aku tandai dia sebagai pihak yang paling mungkin mengatur vote palsu ini.
d|rasanya nggak adil vote dia setelah penjelasannya sudah meluruskan salah paham.
o|dia bukan Spy sungguhan, klaimnya cuma jalan keluar saat terpojok.
d|tolong jangan buang dia. Dia sudah memberikan alibi yang bisa diperiksa.
o|kecurigaanku justru ke dia yang tiba-tiba mempercepat vote tanpa alasan jelas.
d|buat sementara aku pasang badan buat dia; belum ada bukti yang memberatkan.
o|dia terdengar ngarang waktu menyebut hasil skill, jangan jadikan omongannya patokan.
d|aku dapat keterangan yang membebaskan dia dari tuduhan tadi.
o|dia layak divote lebih dulu, pola tuduhannya berubah mengikuti siapa yang ramai diserang.
d|menahan vote ke dia itu masuk akal, alasan telatnya bukan kedok menurutku.
o|nggak usah ikuti arahan dia, aku curiga sengaja dibuat supaya Hitman lolos.
d|tuduhan itu belum cukup untuk menyatakan dia jahat, aku menolak vote tersebut.
o|dia yang paling sus di obrolan ini; klaim barunya malah membatalkan klaim awal.
d|penjelasan soal koneksi sudah cukup buatku, dia tidak perlu dieksekusi.
o|aku pilih dia untuk dikeluarkan, kepanikan menutup diskusinya terasa dibuat-buat.
'''
BANK['witness'] = '''
d|dari cerita {c}, {a} cuma telat mengetik. Aku nggak melihat alasan buat vote {a}.
o|catatan {c} bikin aku curiga ke {a}; urutan aksinya berubah dua kali.
w|hasil Peek yang diklaim {c} tentang aku itu keliru, aku bukan Hitman.
o|aku pakai laporan {c} sebagai petunjuk: {a} yang menurutku berbohong soal Guard.
d|{c} bilang chatnya sempat terkunci; itu menjelaskan diamnya {a}, jangan dicurigai.
o|dengar kesaksian {c} tadi, makin jelas {a} sengaja menggeser vote tanpa alasan.
w|bantahanku ke hasil {c} sederhana: aku Civilian, bukan pelaku yang ditulis di situ.
o|yang kucurigai {a}, bukan sumber ceritanya; {c} cuma mengingatkan soal waktu klaim itu.
d|aku sepaham dengan {c} soal ini, {a} belum layak masuk daftar eksekusi.
o|berdasarkan potongan chat dari {c}, klaim Stalker {a} terdengar palsu.
w|tuduhan {c} nggak membuktikan aku jahat; aku memang Spy dan tidak melakukan Hostage.
o|{a} paling sus buatku setelah baca rangkuman {c}; alasan diamnya berganti lagi.
d|kalau mengikuti urutan yang dicatat {c}, {a} justru bebas dari tuduhan malam itu.
o|aku setuju poin {c}: vote {a}, ceritanya soal Peek bertentangan dengan ucapannya sendiri.
w|aku tidak mengaku Hitman. Kutipan yang dibawa {c} itu cuma bagian kalimatku.
o|info {c} soal pindah pilihan membuatku menandai {a} sebagai pengatur vote ini.
d|{a} aman menurutku, penjelasan yang disampaikan lewat {c} masih konsisten.
o|dari obrolanku dengan {c}, {a} ternyata mengubah target klaimnya; itu mencurigakan.
w|{c} boleh menyebut hasil apa pun, tapi aku tetap bukan Hitman dan nggak layak divote.
o|aku merujuk cerita {c}, dan yang layak dicurigai di situ jelas {a}.
d|jangan lempar vote ke {a}; laporan {c} hanya menjelaskan pesan terlambat, bukan bukti kejahatan.
o|{c} mengingatkan satu detail yang penting: pengakuan {a} palsu menurutku.
w|klaim Peek dari {c} tidak sesuai role-ku, aku Stalker dan tuduhan itu salah.
o|menurut catatan yang dibagikan {c}, {a} tahu detail yang belum dibahas; aku curiga berat.
d|aku percaya pembelaan {a} setelah dengar penjelasan {c}, waktunya masih cocok.
o|jangan keliru sasarannya, dari kesaksian {c} aku justru memilih vote {a}.
w|aku menolak kesimpulan {c} tentang diriku; beda pendapat bukan bukti aku pelaku.
o|{a} seperti menyiapkan alibi palsu, itu kesimpulanku dari cerita {c} tadi.
d|hasil yang diceritakan {c} menunjukkan {a} Civilian, jadi aku bela {a}.
o|yang kutangkap dari info {c}, {a} sengaja menyembunyikan alasan pindah vote.
w|{c} menafsirkan diamku sebagai pengakuan, padahal aku lag. Aku nggak bersalah.
o|aku condong menuduh {a}; kesaksian {c} menyingkap kontradiksi klaimnya.
d|ada penjelasan dari {c} yang membebaskan {a}, jangan lanjutkan tuduhan itu.
o|{c} cuma menyampaikan urutan chat, tetapi urutan itu membuat {a} terlihat bohong.
w|jangan vote aku berdasarkan tuduhan {c} itu; aku tidak punya aksi Hostage.
o|setelah dengar versi {c}, aku rasa {a} bukan Spy, cuma memakai klaim buat lolos.
d|sepemikiran dengan {c} di bagian ini: telat jawab tidak menjadikan {a} Hitman.
o|aku minta vote {a}, mengacu pada perubahan alibi yang dilaporkan {c}.
w|yang dikutip {c} bukan sangkalan role-ku; aku tetap warga dan tidak membunuh siapa pun.
o|cerita {c} memperkuat dugaanku bahwa {a} sedang menutupi pelaku sebenarnya.
d|{a} tidak patut dieksekusi dari bukti itu, {c} sendiri cuma mencatat jeda chat.
o|boleh cek catatan {c}, alasan kenapa aku curiga {a} ada di pergantian klaimnya.
w|aku memang belum membalas pesan {c}, tetapi itu karena sinyalku putus, bukan karena bersalah.
o|hasil yang disebut {c} memberatkan {a}; aku akan taruh vote ke {a}.
d|aku tetap di pihak {a}. Menurut kronologi dari {c}, tidak ada aksi jahat yang terbukti.
o|rangkuman {c} menunjukkan {a} asal menuduh demi lolos dari pemeriksaan; aku nggak percaya {a}.
w|{c} membaca jawabanku terpotong; bagian lengkapnya jelas bilang aku bukan Hitman.
o|pilihanku {a} untuk divote, sesudah kesaksian {c} alibinya makin tidak masuk akal.
d|dari yang disampaikan {c}, alasan koneksi {a} masuk akal. Stop tuduh {a} dulu.
o|{a} kelihatan sedang mengarahkan kita salah vote, apalagi setelah mendengar informasi {c}.
'''
BANK['mixed_relations'] = '''
o|{a} bukan Hitman, justru {b} yang alibinya berubah tiap ditanya.
o|aku vote {b}; sementara {a} jangan ikut diseret, hasil Peek-ku membersihkan dia.
o|meski {a} tadi lambat jawab, dia aman. Yang sus itu {b} dengan klaim Spy mendadaknya.
o|jangan percaya {b} soal hasil malam, tapi {a} masih kubela karena penjelasannya cocok.
o|{a} mungkin bersih menurut catatan ini, sedangkan {b} makin mencurigakan setelah pindah vote.
o|arahin vote ke {b} aja. Untuk {a}, aku sudah cek dan dapat Civilian.
o|dia tidak layak dieksekusi cuma karena diam; {b} malah terkesan ngarang soal Guard.
o|klaim {b} palsu buatku, beda dengan {a} yang klaimnya masih masuk akal dan patut dipercaya.
o|aku lindungi {a} dari vote ini, karena {b} yang jelas-jelas menutupi urutan aksinya.
o|yang perlu dicurigai {b}. Diamnya {a} masih wajar, jangan jadikan tersangka juga.
o|sekalipun {a} lupa ronde, itu bukan bukti dia pelaku; aku lebih curiga pada {b}.
o|jangan ikuti arahan {b}, motifnya aneh. {a} justru bukan pelaku menurut hasilku.
o|dia aman dari Peek yang kulakukan, tetapi {b} mesti diperiksa sebagai calon Hitman.
o|{b} terlalu rapi mengalihkan isu, aku nggak percaya dia; {a} masih kuberi pembelaan.
o|tidak ada dasar vote {a}, sementara kontradiksi cerita {b} sudah cukup bikin aku curiga.
o|aku menuduh {b} sengaja bikin salah vote. Soal {a}, alasan telatnya benar-benar masuk akal.
o|meski belum semua detail keluar, {a} tidak bersalah. Yang kutandai sus adalah {b}.
o|{b} pantas dikeluarkan sekarang; tolong jangan buang {a} yang sudah terkonfirmasi Civilian dari Peek-ku.
o|jangan ganggu dia dengan tuduhan tanpa bukti, justru {b} yang menyembunyikan hasil aksinya.
o|menurutku {b} bohong, sedangkan {a} hanya salah tulis dan tidak layak dicurigai.
o|pembelaanku tetap buat {a}; kalau harus menetapkan pilihan, aku pilih eksekusi {b}.
o|{b} yang memancing role orang lain itu sus. {a} jangan divote, klaimnya bisa kujelaskan.
o|aku rasa {a} bersih walau jawabannya pendek, tapi pola vote {b} seperti cari aman buat Hitman.
o|hasil Peek memberatkan {b}. Untuk {a} hasilnya Civilian, jadi dia aman menurutku.
o|dia bukan dalangnya; {b} yang dari tadi menekan supaya kita cepat salah pilih.
o|aku nggak percaya klaim baru {b}. {a} masih kuanggap warga, tuduhannya belum terbukti.
o|{a} jangan disudutkan karena kena Gag Order; yang aneh malah waktu pengakuan {b}.
o|kalau ada yang pantas dicurigai itu {b}, bukan {a} yang penjelasannya sudah konsisten.
o|aku bela {a} dalam urusan ini, tetapi {b} jelas mengarang alasan kenapa pindah pilihan.
o|{b} masuk daftar vote-ku. {a} keluar dari daftar itu karena aku yakin dia bukan Hitman.
o|bahkan kalau {a} belum buka role, aku tetap menolak vote dia; {b} lebih kelihatan menutup-nutupi.
o|jangan jadikan info {b} pegangan, dia bohong. Klaim {a} justru masuk akal, aku membelanya.
o|dia sempat lag jadi pantas dibela, sedangkan {b} memakai alasan yang bertabrakan dengan chatnya sendiri.
o|aku curiga {b} memasang tuduhan palsu; {a} tidak melakukan aksi yang dituduhkan itu.
o|{a} mungkin aman dan sebaiknya jangan divote dulu. Dorongan vote mendadak {b} malah mencurigakan.
o|eksekusi {b} jadi pilihanku, sementara aku bisa menjamin hasil Peek ke {a} bukan Hitman.
o|salah ketik {a} bukan alasan menghukumnya, tapi cerita {b} terlalu janggal untuk dipercaya.
o|{b} ngaku Stalker padahal hasilnya berubah terus, aku curiga. {a} tetap bersih di mataku.
o|dia layak dapat pembelaan setelah urutannya jelas; {b} yang menurutku sengaja merusak urutan itu.
o|semua keraguanku sekarang ke {b}; {a} sudah menjelaskan jedanya dan tidak patut dituduh.
o|aku menahan vote ke {a} karena dia bukan pelaku, tetapi mendukung vote {b} atas klaim palsunya.
o|jangan percaya {b} yang gonta-ganti cerita. Walau {a} diam, aku tahu dia bukan Hitman.
o|{a} masih bisa dipercaya sebagai warga; kejanggalan justru ada pada gerak vote {b}.
o|{b} sedang mengarang menurutku. Pembelaan {a} layak diterima karena waktunya sesuai catatan.
o|dia tidak pantas diseret ke tuduhan itu, yang punya motif menutup pelaku malah {b}.
o|vote {b} dulu, perubahan hasil Peek-nya nggak wajar. {a} aman, aku sudah dapat hasil Civilian.
o|walaupun {a} belum menjawab panjang, aku yakin dia bersih; {b} malah terlalu sibuk memelintir cerita.
o|aku anggap {b} tersangka utama. Untuk {a}, jangan abaikan bukti yang membersihkannya.
o|aku tidak setuju {a} dieksekusi, tetapi kelakuan {b} menghindari pertanyaan aksi jelas sus.
o|{b} yang patut disorot sebagai Hitman; {a} cuma terlambat membaca dan bukan orang jahat.
'''
BANK['reference_start'] = '''
d|setelah kita urutkan dari awal, dia tidak bersalah; jeda chat tadi bukan bukti aksi Hitman.
o|balik ke orang di pembuka tadi, aku curiga dia sengaja mengacak kronologi.
d|kesimpulanku masih sama: dia jangan divote, penjelasan keterlambatannya bisa diterima.
o|untuk pemain yang dibahas pertama, klaimnya palsu menurutku. Aku akan vote dia.
d|dia aman kok dari hasil Peek-ku; pembahasan waktunya tadi tidak mengubah itu.
o|setelah dengar semua urutan ini, aku malah yakin dia menutupi sesuatu.
d|soal dia yang tadi jadi bahasan awal, aku bela. Salah catat ronde tidak otomatis berarti pelaku.
o|aku kembali ke klaim di awal: dia ngarang, karena dua versinya nggak mungkin sama-sama benar.
d|dia tidak perlu dieksekusi. Dari rangkaian penjelasan tadi tuduhannya sudah gugur.
o|pemain pembuka itu layak dicurigai, dia tahu detail yang seharusnya belum muncul.
d|kembali ke dia, aku nggak melihat alasan buat menganggapnya Hitman hanya dari chat yang putus.
o|yang kusebut sus tetap orang di awal tadi; dia mengulur sampai semua lupa alasan vote.
d|aku masih menolak vote ke dia. Urutan yang kita rapikan justru mendukung alibinya.
o|habis kita cocokkan waktunya, dia ternyata berbohong soal kapan aksinya dilakukan.
d|orang yang kita bahas sejak awal itu bersih menurutku, dia cuma belum selesai mengetik.
o|aku pilih dia sebagai target vote; pembicaraan panjang ini malah memperjelas kontradiksinya.
d|dia bukan Hitman. Klaim yang kita bahas pertama masih cocok dengan catatan yang ada.
o|balik ke kasus pembuka, aku nggak percaya dia punya role seperti yang diklaimnya.
d|buat orang yang namanya muncul pertama tadi, stop tuduh dia dulu; bukti itu lemah.
o|sekarang makin kelihatan dia sengaja mendorong salah vote, bukan sekadar keliru mengingat.
d|jangan kita buang dia setelah bahas sejauh ini, ada penjelasan masuk akal buat jedanya.
o|yang di awal tadi tetap kandidat Hitman bagiku; caranya menyusun alibi terasa dibuat-buat.
d|aku pasang badan buat dia yang kita bahas pertama. Hasil pengecekanku membebaskannya.
o|dia pantas disorot lebih keras, alasan yang diajukan sejak pembuka ternyata saling bertabrakan.
d|kesalahan urutan itu bukan kejahatan. Untuk dia, aku sarankan tahan vote karena dia belum terbukti salah.
o|setelah selingan tadi, aku balik menuduh dia; klaim tentang Peek itu jelas tidak konsisten.
d|pembahasan panjang ini tidak membuat dia layak divote. Aku masih percaya dia warga.
o|aku anggap dia sedang nutupin pelaku, terutama dari cara mengubah alasan pada awal obrolan.
d|dia yang disebut di pesan awal aman dari tuduhan itu, hasilku menunjukkan Civilian.
o|kita kembali ke alibi pembuka. Aku curiga dia mengarang jeda chat supaya lolos.
d|aku bela orang yang pertama dibahas: dia sudah punya alasan wajar, jangan jadikan korban vote.
o|tidak usah percaya dia soal aksi malam itu. Dari rangkaian tadi klaimnya terlihat palsu.
d|aku rasa dia bersih, bukan seperti yang dikhawatirkan di awal. Catatannya masih masuk akal.
o|kalau keputusan harus dibuat, aku vote dia yang jadi topik awal karena alasannya janggal.
d|balik ke nama pembuka tadi, dia tidak perlu membayar kesalahan baca kita dengan dieksekusi.
o|dia itu sus menurutku; terlalu banyak penjelasan baru yang menabrak klaim pertamanya.
d|orang di awal jangan dimasukkan daftar tersangka lagi, aku percaya dia bukan pelaku.
o|aku menilai dia bohong dari awal, makanya detail aksinya terus berubah selama dibahas.
d|lihat lagi pembahasan pertama, dia sekadar salah ingat dan tidak patut dicurigai.
o|vote-ku tetap ke dia. Kronologi awalnya terlalu berlubang untuk dianggap alibi yang sah.
d|dia belum tentu melakukan apa pun, jadi aku menolak eksekusi orang yang disebut awal tadi.
o|untuk orang yang dibahas sebelum selingan, aku yakin dia memakai klaim role palsu.
d|aku tidak menganggap dia jahat setelah membaca ulang konteks awal, alasan koneksinya wajar.
o|dia sengaja memutar pembicaraan soal pilihannya, dan itu cukup bikin aku curiga berat.
d|hasil yang kumiliki membersihkan dia, orang yang sejak pembuka kita bicarakan itu.
o|kembali ke pemain pertama tadi: pola jawabnya mencurigakan, aku mendukung vote dia.
d|jangan tuduh dia dari perkiraan waktu saja, masih ada pembelaan yang masuk akal untuknya.
o|aku makin meragukan kejujurannya, dia seperti sudah menyiapkan jawaban palsu sejak awal.
d|akhirnya aku tetap membela dia. Tidak ada alasan kuat untuk membuang pemain pembuka itu.
o|kita sudah bahas cukup panjang; dia yang di awal itu menurutku paling layak dieksekusi.
'''
BANK['self'] = '''
d|aku tadi cuma baca ulang chat, bukan sedang menyusun aksi Hitman. Jangan vote aku.
o|kalau kalian butuh keputusan sekarang, vote aku saja. Aku terima hasilnya.
d|gw bukan pelakunya, pesan yang telat muncul itu gara-gara sinyal di tempatku.
o|daripada perdebatan ini muter, aku rela dikeluarkan lewat vote sekarang.
d|aku Spy, jadi tuduhan kalau aku yang melakukan Hostage itu nggak cocok.
o|ya sudah, taruh semua pilihan ke aku. Biar aku yang keluar ronde ini.
d|jangan anggap aku bersalah cuma karena belum mengetik, koneksiku baru balik.
o|aku menyerah menjelaskan; silakan vote aku, keputusan itu kuterima tanpa protes.
d|aku tidak punya aksi menyerang. Klaim Civilian-ku bukan alasan buat memfitnah aku.
o|kalau memang harus ada yang dieliminasi, pilih aku aja sekarang.
d|yang kulakukan tadi cuma membaca urutan vote, aku bukan Hitman yang kalian cari.
o|vote diriku saja biar diskusinya selesai, aku nggak akan membantah lagi.
d|aku lambat balas karena pindah jaringan, bukan karena mencari alibi.
o|aku ikhlas jadi yang dikeluarkan. Kalian boleh mengunci vote ke aku.
d|role-ku Stalker; aku tidak bersalah, nanti hasil pengecekanku bisa dibahas.
o|nggak usah menunggu jawabanku lagi, eksekusi aku saja lewat vote.
d|aku memang lupa nomor ronde, tetapi itu tidak menjadikan aku pelaku Hostage.
o|kalau itu bikin permainan jalan, aku bersedia divote keluar sekarang.
d|tuduhan ke aku meleset, tadi chatku terkirim sebagian karena jaringan putus.
o|aku terima jadi sasaran akhir. Arahkan vote kalian ke aku.
d|jangan buang aku dulu, aku Civilian dan tidak pernah punya aksi malam.
o|aku sudah nggak mau debat, vote aku saja dan lanjutkan rondenya.
d|aku nggak bohong soal role, cuma belum sempat nulis penjelasan lengkap.
o|biar aku yang kalah vote kali ini, pilih namaku tanpa perlu tunggu lagi.
d|aku tidak melakukan Gag Order; jeda pesanku cuma karena aplikasi sempat macet.
o|kalau kalian curiga kepadaku, aku rela dieksekusi. Vote aku sekarang juga boleh.
d|aku bukan orang jahat. Satu jawaban pendek tadi jangan dijadikan bukti melawanku.
o|sudah, aku saja yang dikeluarkan. Aku menerima pilihan itu.
d|sinyalku naik turun dari tadi, makanya aku baru bisa menjawab sekarang.
o|aku menawarkan diri buat divote, tidak perlu menunda keputusan demi aku.
d|aku klaim Spy dan menolak tuduhan itu, aksiku bukan untuk menyandera.
o|tetapkan saja aku sebagai pilihan vote terakhir, aku sudah pasrah.
d|aku tidak ngarang hasil Peek, jadi jangan eksekusi aku sebelum catatanku terbaca.
o|aku nggak keberatan keluar duluan; kalau butuh sasaran vote, pakai namaku.
d|aku tadi diam karena lagi lag berat, bukan sedang sembunyi sebagai Hitman.
o|silakan akhiri bagianku di ronde ini, aku minta kalian vote aku saja.
d|aku cuma salah pencet kirim. Aku tidak bersalah seperti dugaan kalian.
o|aku pilih menyerah dan menerima eliminasi, arahkan suara kalian kepadaku.
d|percaya atau nggak, aku Civilian; jangan menuntut hasil skill yang memang nggak kupunya.
o|biar cepat, aku siap jadi korban vote kalian. Aku menerima tanpa syarat.
d|aku bukan Hitman, alasan aku menunggu tadi karena belum selesai membaca laporan.
o|nggak apa aku dibuang sekarang, jadikan aku pilihan vote ronde ini.
d|aku masih membela diriku, tuduhan itu cuma mengulang potongan pesanku tanpa konteks.
o|aku nggak akan menahan keputusan, vote aku dan selesaikan pembahasan ini.
d|jangan seret aku jadi pelaku, layar chatku membeku saat kalian mulai diskusi.
o|jika kalian ingin menuntaskan vote, aku siap dikeluarkan. Pilih aku.
d|aku Stalker, bukan Hitman. Jangan paksa aku mengaku melakukan aksi yang bukan milikku.
o|aku pasrah saja kali ini; semua vote boleh ditujukan kepadaku.
d|keterlambatanku bukan kode apa-apa, aku sempat kehilangan koneksi dan tidak bersalah.
o|aku menerima hasil terburuknya. Daripada menunggu, vote aku keluar sekarang.
'''
BANK['short_history_1'] = '''
d|aku bukan Hitman, satu pesan yang terlambat bukan bukti aku pelakunya.
o|{a} yang baru klaim itu sus, alasannya terlalu dibuat-buat.
d|jangan vote aku dari dugaan itu, aku tidak melakukan Hostage.
n|aku klaim Civilian; itu informasi role-ku buat pertanyaanmu tadi.
d|aku nggak ngumpet, sinyal di sini putus sejak diskusi dibuka.
o|aku curiga kamu ngarang hasil itu, klaimnya kelewat yakin.
d|tuduhan barusan tidak benar, aku Spy dan bukan penyerangnya.
n|{a}, hasil Peek yang disebut tadi keluar pada ronde berapa?
d|aku belum sempat ketik karena aplikasiku macet, bukan karena bersalah.
o|vote {a} aja, pernyataannya soal skill nggak masuk akal.
d|aku Stalker, tolong jangan paksa aku mengakui aksi Hitman.
n|jawabanku untuk pertanyaan itu: aku menggunakan Guard pada malam kedua.
d|aku tidak punya skill menyerang, jadi jangan arahkan kesalahan itu kepadaku.
o|kamu terdengar bohong soal role, aku nggak percaya klaim barusan.
d|yang ditulis tadi cuma potongan ucapanku. Aku nggak bersalah.
n|{a}, kamu masih bisa mengetik sekarang atau chat sedang terkunci?
d|aku baru masuk lagi setelah jaringan terputus, jangan jadikan jeda itu tuduhan.
o|aku menandai {a} sebagai calon Hitman karena klaimnya janggal.
d|sumpah aku bukan pelaku, alasan vote ke aku belum punya bukti.
n|aku Spy. Itu jawaban soal role yang kamu tanyakan kepadaku.
d|aku memang belum kasih detail, tapi itu bukan berarti aku Hitman.
o|klaim kamu palsu menurutku, terlalu banyak detail yang dipaksakan.
d|jangan buang aku, hasil Peek-ku bisa dipakai buat meluruskan tuduhan ini.
n|{a} menyebut malam pertama; aku mau tanya apakah nomor rondenya sudah benar.
d|aku tidak ngarang, kesalahan nomor itu cuma salah ketik dari aku.
o|{a} yang harus kita vote sekarang, cerita barusan terasa seperti alibi palsu.
d|aku warga biasa, jadi berhenti menuntut bukti skill dariku.
n|aku belum memakai Peek. Itu yang bisa kujawab untuk pertanyaanmu.
d|aku menolak tuduhan tadi; chatku terpotong, bukan sengaja menyembunyikan aksi.
o|aku curiga kamu sengaja memakai klaim itu buat menghindari vote.
d|aku bukan Hitman hanya karena tidak ikut ramai, aku sedang membaca pesan yang tertinggal.
n|boleh jelaskan urutan aksi malamnya, {a}? Aku sedang mencatat.
d|role-ku Spy, dan tuduhan melakukan Gag Order itu salah alamat.
o|jangan percaya pengakuan {a}, kedengarannya cuma cari aman.
d|aku telat karena koneksi, bukan karena menunggu tuduhan reda.
n|aku Civilian dan tidak ada aksi malam untuk kulaporkan, menjawab pertanyaanmu tadi.
d|tuduhan ini nggak mengubah faktanya: aku tidak menyandera siapa pun.
o|kamu paling mencurigakan buatku dari klaim pertama itu, aku pilih vote kamu.
d|jangan salah baca, aku bilang bukan Hitman. Aku tidak mengaku jadi pelaku.
n|{a}, apakah hasil yang disebut tadi teks lengkap atau ringkasan?
d|aku tidak sedang cari alasan, ponselku sempat kehilangan sinyal saat chat dimulai.
o|aku nggak beli cerita {a}; klaimnya terlalu pas untuk lepas dari tuduhan.
d|aku tetap menyangkal tuduhan itu, tidak ada aksi menyerang yang bisa kulakukan.
n|untuk pertanyaan yang ditujukan kepadaku, aku menggunakan Guard tadi malam.
d|aku Stalker dan bukan orang jahat, jangan buru-buru kunci vote ke aku.
o|kamu ngarang soal hasil malam itu menurutku, aku justru makin curiga.
d|aku tidak bersalah. Diam sebentar tadi karena pesan belum selesai kubaca.
n|{a} tadi menyebut Guard; bisa sebutkan malam keberapa tanpa membuka nama target?
d|aku cuma belum selesai menjawab, bukan berarti tuduhan Hitman itu benar.
o|{a} patut dicurigai dari cara mengaku role itu, rasanya seperti menyiapkan tameng.
'''
BANK['second_person'] = '''
d|menjawab yang minta penilaian tadi: kamu aman menurut Peek-ku, nggak perlu takut vote.
o|balik ke yang bertanya soal klaimnya, aku curiga kamu memakai role palsu.
d|untuk kamu yang minta aku menilai alibimu, aku percaya kamu bukan pelaku.
o|lu yang tadi minta pendapatku itu justru sus, klaimnya terlalu sering berubah.
d|kalau yang minta tanggapan tadi masih baca, kamu jangan menyerah; aku menolak vote ke kamu.
o|jawabanku soal alibimu: kamu berbohong menurutku, jadi aku akan vote kamu.
d|kamu yang mengajukan penjelasan tadi kubela, telat membaca bukan bukti jadi Hitman.
o|aku kembali ke pertanyaan sebelum selingan: lu sedang menutup-nutupi aksi, ya? Aku curiga.
d|buat yang tadi bertanya padaku, kamu tidak pantas dieksekusi dari bukti selemah itu.
o|penilaianku ke kamu yang minta dicek itu buruk, klaim Guard-mu terdengar palsu.
d|aku jawab permintaanmu tadi, kamu bersih dari hasil pengecekanku.
o|yang meminta komentarku sebelum pesan timer tadi: kamu makin sus setelah ganti alasan.
d|untuk alibi yang kamu minta kubaca, aku percaya kamu; itu bukan alasan melakukan vote.
o|kamu yang menyapa aku tadi sepertinya ngarang. Aku tidak percaya klaim Stalker-mu.
d|aku masih menjawab orang yang minta penilaian, ya: kamu bukan Hitman menurut hasilku.
o|kalau kamu masih menunggu jawabanku soal klaim tadi, aku pilih mencurigai kamu.
d|soal pertanyaan tentang dirimu barusan, lu nggak perlu divote; keterlambatanmu masuk akal.
o|aku jawab yang bertanya sebelum pengumuman waktu: kamu seperti sengaja bikin alibi palsu.
d|buat kamu yang tadi meminta pembacaan catatan, tuduhan ke kamu belum terbukti; aku bela.
o|lu minta aku menilai, kan? Menurutku kamu mengubah cerita buat meloloskan diri.
d|jawaban untuk pertanyaan sebelum selingan itu: aku tidak setuju kamu dikeluarkan, kamu aman.
o|kamu yang tadi minta pendapatku soal role malah bikin aku curiga, klaimnya nggak nyambung.
d|aku menanggapi permintaanmu lagi: penjelasan kamu bisa dipercaya dan aku menolak vote itu.
o|untuk kamu yang barusan menanyakan penilaianku, aku vote kamu karena ceritamu janggal.
d|balik menjawab yang minta dicek, kamu tidak bersalah dari catatan yang kubaca.
'''
BANK['plural_reference'] = '''
d|jangan suudzon dulu {c}, mereka berdua aman menurut hasil pengecekanku.
o|aku curiga keduanya kompak mengarahkan vote supaya pelaku lolos.
d|mereka bukan Hitman, catatan Peek-ku justru menyebut keduanya Civilian.
o|{c}, yang perlu dicurigai itu mereka berdua; cerita mereka terlalu seragam dan janggal.
d|aku menolak vote ke keduanya, telat jawab bareng bukan bukti mereka satu kubu jahat.
o|mereka sama-sama ngarang soal aksi malam, aku nggak percaya dua klaim itu.
d|sabar {c}, jangan eksekusi mereka hanya karena belum menjelaskan panjang.
o|lebih baik vote keduanya, masing-masing mengubah alibi setelah ditanya lagi.
d|keduanya masih kubela, jeda chat itu tidak membuktikan ada aksi Hitman.
o|aku nggak percaya mereka, cara saling menutup pertanyaannya terlalu mencurigakan.
d|tolong dengar dulu {c}, mereka aman; aku sudah dapat hasil yang membersihkan keduanya.
o|dua orang itu jelas sus, mereka menggeser pilihan tanpa satu pun alasan masuk akal.
d|keduanya bukan pelaku menurutku, klaim mereka masih cocok dengan urutan malam.
o|{c}, jangan termakan cerita mereka berdua; klaimnya terdengar palsu.
d|aku percaya mereka warga biasa. Kita tidak punya alasan mengeksekusi keduanya.
o|mereka kompak cari kambing hitam, aku pilih keduanya masuk daftar vote.
d|jangan terburu-buru {c}, keduanya hanya salah menulis ronde dan belum patut dicurigai.
o|klaim mereka tidak bisa dipercaya, keduanya seperti sudah menyiapkan kebohongan yang sama.
d|buatku mereka berdua bersih, hasil Peek tidak menunjukkan Hitman pada salah satunya pun.
o|keduanya harus dicurigai, perubahan cerita mereka terlalu besar buat sekadar lupa.
d|{c}, aku pasang badan untuk mereka; dua tuduhan tadi tidak punya bukti.
o|aku mendukung vote ke mereka berdua, masing-masing berusaha menutupi detail aksinya.
d|mereka tidak bersalah hanya karena masih menahan role, jangan buang keduanya dulu.
o|yang perlu diperiksa sebagai calon Hitman itu mereka, {c}; dua alibinya sama-sama janggal.
d|aku tetap bela keduanya, obrolan yang terpotong tidak menjadikan mereka pelaku.
'''
BANK['rhetorical_question'] = '''
d|masa sih kamu Hitman cuma gara-gara salah ketik? Aku nggak setuju vote itu.
o|orang kayak lu ngaku Spy tapi menghindar terus, jangan-jangan klaimmu ngarang?
d|apa pantas kamu dieksekusi hanya karena chat lambat? Jelas aku bela kamu.
o|kamu mengaku Civilian kok tahu detail aksi itu? Mencurigakan banget.
d|kalau alasan koneksimu masuk akal, kenapa kamu harus dituduh? Kamu bukan pelaku menurutku.
o|lu pikir klaim yang berubah itu nggak kelihatan? Aku curiga kamu bohong.
d|masa kamu jadi tersangka hanya karena belum selesai baca? Jangan vote kamu dulu lah.
o|kamu yakin kami percaya cerita sepalsu itu? Aku rasa kamu Hitman.
d|bukankah hasil Peek-ku sudah membersihkan kamu? Nggak ada alasan buang kamu.
o|kok kamu baru mengaku Stalker setelah terdesak? Rasanya cuma kedok, deh.
d|apa semua yang diam harus divote, termasuk kamu? Aku menolak, kamu belum terbukti jahat.
o|kayak lu yang gonta-ganti alibi masih mau dipercaya? Aku sih vote kamu.
d|masa satu nomor ronde keliru bikin kamu pelaku? Aku percaya penjelasanmu.
o|kamu diam pas ditanya aksi karena tahu kebohongannya terbongkar, ya? Sus banget.
d|kalau cuma terlambat mengetik, apa adil kamu dieksekusi? Aku membela kamu di sini.
o|kok hasil Peek kamu selalu cocok dengan arus vote? Aku curiga kamu mengarangnya.
d|bukannya kamu sudah menjelaskan soal lag? Tuduhan Hitman ke kamu nggak beralasan.
o|kamu mengira perubahan target mendadak itu wajar? Buatku jelas mencurigakan.
d|masa sih kamu perlu dibuang padahal hasilku Civilian? Aku tidak mau vote kamu.
o|lu menghindari alasan pindah vote lagi, memang takut ketahuan sebagai pelaku?
d|apa salahnya kamu nunggu chat terbaca dulu? Aku yakin kamu bukan Hitman.
o|kalau kamu benar Spy, kenapa ceritanya tabrakan begitu? Jangan-jangan klaim palsu lagi.
d|bukankah tuduhan ke kamu cuma perkiraan? Aku tetap pasang badan buat kamu.
o|masa kami harus percaya kamu setelah alibi itu berubah tiga kali? Aku malah makin curiga.
d|kamu pantas dicurigai cuma karena balas singkat? Nggak lah, aku percaya kamu bersih.
'''
BANK['agreement'] = '''
d|sepemikiran dengan {c}, aku dukung kesimpulan yang tadi disampaikan.
o|iya, aku setuju penilaian itu. Masukkan yang dibahas tadi ke daftar vote.
d|yang disampaikan {c} masuk buatku, aku ada di pihak yang sama soal tuduhan tadi.
o|aku sependapat dengan {c}; kecurigaan itu cukup kuat untuk diteruskan.
d|betul, kesimpulan sebelum pesan waktu itu juga yang kupegang.
o|setuju sama yang barusan menjelaskan, pilihan vote itu masuk akal.
d|aku ikut pendapat {c} di atas, pembelaannya layak diterima.
o|ya, itu juga alasanku dari tadi. Aku mendukung tuduhan yang sama.
d|nggak setuju tuduhan {c} tadi, bukti yang disebut belum cukup buat mengeksekusi orang itu.
o|sepaham dengan {c}, aku juga merasa ada yang janggal pada orang yang dibahas.
d|aku menolak kesimpulan menuduh yang tadi, alasan itu masih bisa dijelaskan dengan wajar.
o|bener, aku ikut vote yang diusulkan sebelum selingan waktu tadi.
d|iya, bela saja dulu seperti saran {c}; aku tidak mau ikut tuduhan tanpa dasar itu.
o|pendapatku sama dengan {c}, jangan percaya klaim orang yang sedang dibicarakan itu.
d|aku juga berpikir begitu, kesimpulan yang membersihkan tadi patut dipakai.
o|ya, tuduhan barusan persis dengan kecurigaanku. Aku setuju.
d|bantahanku sama dengan {c}: tuduhan ke orang tadi tidak punya pegangan.
o|aku dukung usulan itu, yang dicurigai tadi memang layak divote.
d|setuju, jangan menghukum orang yang dibahas cuma dari jeda chat seperti penjelasan {c}.
o|sependapat soal klaim palsu itu, aku ada di sisi {c} untuk keputusan vote ini.
d|aku nggak ikut menuduh seperti {c}; alasan tersebut belum menjadikan orang tadi pelaku.
o|iya, yang {c} soroti itu juga terasa paling sus buatku.
d|betul sekali, aku mempertahankan pembelaan yang disampaikan tadi.
o|pilihanku mengikuti kesimpulan sebelum timer itu, aku setuju tuduhannya.
d|aku menolak ajakan vote {c}, kita masih punya alasan untuk membela orang yang dibicarakan.
'''
BANK['multiple_targets'] = '''
d|{a} dan {b} sama-sama bersih dari hasil Peek-ku, jangan vote mereka.
o|aku curiga {a} bareng {b}; alibi keduanya kelihatan disusun untuk menutup kejadian malam.
d|jangan seret {a} maupun {b} jadi pelaku hanya karena chatnya belum lengkap.
o|vote {b} dan {a} jadi pilihanku, dua klaim itu bertentangan dengan catatan.
d|{a} bukan Hitman, {b} juga aman. Aku dapat hasil Civilian untuk keduanya.
o|klaim {a} palsu dan pengakuan {b} sama nggak masuk akalnya, aku tidak percaya dua-duanya.
d|aku membela {b} sekaligus {a}, keterlambatan mereka bukan bukti aksi jahat.
o|yang sus menurutku {a} serta {b}, mereka kompak menghindari pertanyaan tentang vote.
d|{a} jangan dieksekusi dulu; {b} juga tidak pantas dihukum dari bukti selemah itu.
o|aku memasukkan {b} dan {a} ke kandidat Hitman, perubahan alasan mereka janggal.
d|dua tuduhan itu meleset, {a} dan {b} hanya salah menulis nomor ronde.
o|{a} aku curigai karena alibinya bolong, sementara {b} juga ngarang soal hasil Peek.
d|di pihak {b} dan {a} aku berdiri, keduanya belum terbukti melakukan Hostage.
o|tolong arahkan vote ke {a} dan {b}; klaim mereka terdengar seperti kedok.
d|aku yakin {a} bersih dan {b} bukan pelaku, penjelasan waktunya masih cocok.
o|{b} itu bohong menurutku, begitu juga {a} yang ceritanya ikut berubah.
d|jangan buang {a} ataupun {b}, ada hasil pengecekanku yang membersihkan mereka.
o|yang pantas disorot {b} bersama {a}, dua-duanya berusaha mempercepat salah vote.
d|{a} aman dari tuduhan ini. Untuk {b}, aku juga menolak vote karena alibinya masuk akal.
o|aku nggak percaya {a} dan {b}, pola saling menutup pertanyaannya terlalu mencurigakan.
d|{b} serta {a} bukan orang jahat menurutku, satu chat terpotong tidak membuktikan sebaliknya.
o|pilihanku mengeksekusi {a} dan {b}, masing-masing punya klaim aksi yang palsu.
d|aku meminta pembelaan untuk {a} juga {b}; keduanya cuma terlambat membaca pesan.
o|{b} makin sus, dan {a} juga tak kalah janggal karena berubah alasan soal Guard.
d|jangan ada vote ke {b} maupun {a} dari dugaan itu, mereka masih bisa dipercaya.
'''
BANK['interruption'] = '''
d|balik ke yang tadi, aku bukan Hitman. Jangan jadikan chatku yang terlambat alasan vote.
o|oke, waktunya sudah jelas. Sekarang aku curiga {a} yang klaimnya berubah dua kali.
d|setelah selingan timer itu, aku tetap bela {a}; penjelasan koneksinya masuk akal.
o|lanjut pembahasan sebelumnya, {a} layak divote karena alibi malamnya janggal.
d|balik lagi, aku Stalker dan bukan pelaku; tuduhan sebelum bahas waktu itu salah.
o|cukup soal sisa menitnya, aku nggak percaya {a} yang hasil Peek-nya berganti terus.
d|untuk orang yang kita bahas tadi, dia aman dari hasilku. Jangan dikeluarkan dulu.
o|kembali ke {a}: makin kupikir, makin terlihat klaim Spy itu palsu.
d|tadi kepotong urusan ronde, tapi aku tetap menyangkal melakukan Hostage.
o|sebelum waktu habis, aku pilih vote {a}; penjelasan aksinya nggak cocok.
d|aku lanjut soal {a}, jangan tuduh dia hanya karena sempat tidak bisa mengetik.
o|selingan tadi nggak mengubah pilihanku, {a} masih paling sus karena menghindari alasan vote.
d|balik ke tuduhan ke aku sebelum timer, aku cuma lag dan bukan sedang menyembunyikan aksi.
o|soal yang dibahas sebelum jam itu, dia berbohong menurutku. Aku mendukung vote ke dia.
d|aku kembali membela {a}; selisih waktu baca bukan bukti bahwa dia Hitman.
o|kita lanjut lagi, klaim {a} tidak masuk akal dan aku menandainya sebagai calon pelaku.
d|aku belum selesai tadi: jangan vote aku, role-ku Civilian dan tidak punya skill menyerang.
o|waktu memang pendek, tapi alasanku vote {a} tetap karena klaimnya palsu, bukan karena buru-buru.
d|balik ke orang tadi, dia tidak bersalah dari catatan Peek-ku. Tolong tahan vote itu.
o|setelah jeda obrolan waktu, kecurigaanku masih ke {a} yang alibinya makin berantakan.
d|melanjutkan jawabanku yang terputus, aku bukan Hitman; jaringan membuat pesan tadi tertunda.
o|aku ingin kembali menyorot {a}, motifnya mempercepat vote terasa seperti melindungi pelaku.
d|tentang {a} yang dibahas sebelum selingan, aku percaya dia warga dan menolak eksekusinya.
o|oke timer lanjut, aku akan vote {a}. Cerita soal Guard-nya kedengaran ngarang.
d|sebelum topiknya hilang, aku tetap membela diriku; tuduhan awal tadi tidak punya dasar.
'''
BANK['first_message_unknown'] = '''
d|dia jangan langsung dicurigai dari awal, kita belum punya bukti apa-apa.
o|aku curiga kamu, ada kesan sedang cari aman di sini.
d|aku belum mau vote dia, orangnya belum terbukti jahat.
o|dia kelihatan sus buatku, aku mau mengawasi dia lebih dulu.
d|kamu belum pantas dianggap Hitman hanya dari kesan pertama.
o|aku akan pilih dia kalau harus menentukan kandidat vote sekarang.
d|jangan buru-buru menaruh tuduhan ke dia, aku rasa dia bukan pelaku.
o|lu tampak seperti Hitman yang sedang menyamar, aku curiga.
d|aku pasang badan buat kamu dulu, nggak ada alasan kuat menuduhmu.
o|menurutku dia yang layak dicurigai dari pembukaan ini.
d|dia masih kuanggap warga, jangan langsung keluarkan tanpa bukti.
o|aku nggak percaya kamu, rasanya ada niat mengarahkan permainan ke jalan salah.
d|lu aman menurut penilaianku, aku nggak akan ikut vote lu sekarang.
o|dia punya gelagat mencurigakan, aku memasukkannya ke daftar calon Hitman.
d|buatku dia bukan musuh, jadi jangan mulai dengan menjadikannya sasaran vote.
o|aku ingin vote kamu dulu, ada sesuatu yang sus dari kesanmu.
d|aku bela dia pada awal ini, praduga saja belum cukup untuk eksekusi.
o|dia kelihatan sedang menyusun kedok, aku tidak mau mempercayainya.
d|kamu bukan Hitman menurutku; jangan sampai kita salah menuduh dari awal.
o|yang kucurigai pertama itu lu, jangan anggap aku bakal percaya begitu saja.
d|dia tidak patut dibuang sebelum kita tahu apa pun, aku menolak vote itu.
o|aku tandai dia sebagai kandidat utama untuk dicurigai sekarang.
d|aku akan melindungi kamu dari vote terburu-buru, belum ada bukti kamu pelaku.
o|kamu terkesan sedang mencari cara menutup pelaku, itu bikin aku waspada.
d|aku masih percaya dia orang baik, jangan jadikan dia pilihan eksekusi pertama.
'''
BANK['neutral_status'] = '''
n|{a}, kamu mengaku role apa untuk ronde ini?
n|aku Spy, menjawab pertanyaanmu barusan soal role.
n|kamu menggunakan Guard pada malam keberapa? Aku cuma mencatat urutannya.
n|aku ingin memastikan klaim {a}, apakah tadi menyebut Stalker atau Civilian?
n|untuk pertanyaan kepadaku tadi, aku klaim Civilian.
n|hasil Peek kamu berupa nama role atau cuma keterangan lain?
n|{a} sudah menyebut status chatnya, sekarang apakah {b} juga bisa mengetik?
n|jawabanku singkat: aku Stalker dan sudah menggunakan Peek sekali.
n|kamu masih bisa memakai skill malam ini atau sudah menggunakannya?
n|boleh catat klaim {a} sebagai Spy dulu, belum ada kesimpulan lain.
n|aku memakai Guard pada malam pertama, itu jawaban pertanyaanmu.
n|kamu sedang melaporkan hasil skill atau baru menyatakan role?
n|{a}, waktu menyebut status tadi maksudnya role atau akses chat?
n|aku belum memakai Peek; itu informasi yang kamu minta dariku.
n|klaim kamu tadi Civilian, betul? Aku ingin menyalin tanpa salah tulis.
n|apakah {a} dan {b} sudah menyampaikan role masing-masing di ronde ini?
n|menjawab pertanyaan soal aksiku, aku memilih Guard tadi malam.
n|kamu ingin menuliskan hasil Peek lengkap atau cukup ringkasannya?
n|{a} tadi mengaku Stalker. Kapan pengakuan itu pertama kali ditulis?
n|aku Civilian, tidak ada aksi malam untuk dilaporkan ke pertanyaanmu itu.
n|kamu masih menunggu giliran membuka klaim atau sudah selesai?
n|aku mau konfirmasi nama pada catatan: {a} yang mengaku Spy tadi, kan?
n|aku menggunakan Peek malam kedua, sesuai pertanyaanmu tentang waktunya.
n|kamu menyebut chat terbuka lagi, itu sebelum atau sesudah pergantian ronde?
n|{a}, boleh tuliskan role yang ingin dicatat tanpa menyebut target skill dulu?
'''

def entries(case):
    return [line.strip().split('|',1) for line in BANK[case].strip().splitlines()]
