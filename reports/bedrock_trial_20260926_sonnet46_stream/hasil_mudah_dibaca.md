# Hasil trial Sonnet 4.6 (streaming) — 50 contoh

Lolos 34, ditolak 16. Pesan terakhir (bertanda **>>**) adalah contoh utama; pesan di atasnya adalah chat_sebelumnya.

## 1. original — label sumber: defend — LOLOS

Pemain: Player1

Teks sumber asli: _bukan aku yang nyandera, gw bukan hitman_

**>>** **Player1**: bukan aku yang nyandera, gw bukan hitman  
   ↳ `defend` → Player1 (defend)

## 2. explicit — label sumber: offend — DITOLAK — Kasus eksplisit harus menyebut nama target di pesan sekarang.

Pemain: Renata, Dimas

1. **Renata**: aku tadi Stalker, sudah Peek ke arah Dimas malam ini  
   ↳ `neutral` → -
**>>** **Dimas**: klaim Stalker kamu tidak masuk akal, hasil Peek kamu ke aku pasti bohong  
   ↳ `offend` → Renata (offend)

## 3. reference_start — label sumber: defend — DITOLAK — Posisi penyebutan dan target belum sesuai kasus.

Pemain: Hendra, Sari, Bagas, Tomi

1. **Sari**: Hendra bilang dia Stalker dan sudah Peek ke Bagas semalam  
   ↳ `neutral` → -
2. **Tomi**: oh ya? apa hasilnya?  
   ↳ `neutral` → -
3. **Sari**: katanya Bagas terlihat bergerak mencurigakan  
   ↳ `neutral` → -
4. **Bagas**: itu tidak akurat, aku tidak kemana-mana  
   ↳ `defend` → Bagas (defend)
5. **Tomi**: Hendra memang sering klaim hal yang tidak bisa dibuktikan  
   ↳ `offend` → Hendra (offend)
6. **Sari**: aku juga ragu sih, tapi belum bisa langsung vote  
   ↳ `neutral` → -
7. **Bagas**: kita tunggu penjelasan lebih dulu  
   ↳ `neutral` → -
8. **Tomi**: setuju, tapi tetap perlu dipertanyakan  
   ↳ `neutral` → -
9. **Sari**: iya, kita lihat saja nanti  
   ↳ `neutral` → -
10. **Bagas**: kalau memang Stalker, harusnya bisa kasih detail lebih spesifik  
   ↳ `neutral` → -
11. **Tomi**: benar, detail itu penting untuk verifikasi  
   ↳ `neutral` → -
12. **Sari**: aku masih menunggu penjelasan dari yang bersangkutan  
   ↳ `neutral` → -
**>>** **Hendra**: aku tidak bohong, hasil Peek itu memang yang aku lihat sendiri  
   ↳ `defend` → Hendra (defend)

## 4. reference_middle — label sumber: offend — DITOLAK — Posisi penyebutan dan target belum sesuai kasus.

Pemain: Laras, Fikri, Nando, Putri

1. **Laras**: diskusi dimulai, siapa yang mau buka suara duluan?  
   ↳ `neutral` → -
2. **Nando**: aku tidak ada informasi khusus malam ini  
   ↳ `neutral` → -
3. **Putri**: sama, aku juga tidak dapat apa-apa  
   ↳ `neutral` → -
4. **Laras**: baik, kita diskusi dari yang paling mencurigakan saja  
   ↳ `neutral` → -
5. **Nando**: menurutku tidak ada yang terlalu menonjol sejauh ini  
   ↳ `neutral` → -
6. **Putri**: Fikri langsung bela diri sebelum ada yang nuduh, itu aneh  
   ↳ `offend` → Fikri (offend)
7. **Laras**: iya, aku juga perhatikan itu tadi  
   ↳ `offend` → Fikri (offend)
8. **Nando**: mungkin dia memang gugup saja  
   ↳ `defend` → Fikri (defend)
9. **Putri**: gugup atau tidak, pembelaan terlalu cepat itu tetap mencurigakan  
   ↳ `offend` → Fikri (offend)
10. **Laras**: kita tanya langsung saja ke dia  
   ↳ `neutral` → -
11. **Nando**: setuju, biar dia jelaskan sendiri  
   ↳ `neutral` → -
12. **Putri**: aku tunggu penjelasannya  
   ↳ `neutral` → -
**>>** **Fikri**: pembelaan terlalu cepat? aku hanya ingin ikut diskusi sejak awal, itu wajar  
   ↳ `offend` → Putri (offend)

## 5. reference_end — label sumber: defend — LOLOS

Pemain: Wulan, Arif, Citra, Bimo

1. **Wulan**: ada yang mau klaim role sekarang?  
   ↳ `neutral` → -
2. **Citra**: aku Civilian biasa, tidak punya informasi khusus  
   ↳ `neutral` → -
3. **Bimo**: aku juga tidak ada klaim khusus  
   ↳ `neutral` → -
4. **Wulan**: baik, kita lihat siapa yang paling mencurigakan  
   ↳ `neutral` → -
5. **Citra**: belum ada yang terlalu menonjol menurutku  
   ↳ `neutral` → -
6. **Bimo**: iya, diskusi masih awal  
   ↳ `neutral` → -
7. **Wulan**: kita tunggu saja perkembangan  
   ↳ `neutral` → -
8. **Citra**: ada yang perlu dibahas lebih lanjut?  
   ↳ `neutral` → -
9. **Bimo**: belum ada dari aku  
   ↳ `neutral` → -
10. **Wulan**: aku juga belum punya info baru  
   ↳ `neutral` → -
11. **Citra**: kita tunggu yang lain bicara  
   ↳ `neutral` → -
12. **Bimo**: Arif klaim Spy tapi belum ada bukti yang mendukung klaimnya  
   ↳ `offend` → Arif (offend)
**>>** **Arif**: klaim aku memang belum bisa dibuktikan sekarang, tapi bukan berarti aku bohong  
   ↳ `defend` → Arif (defend)

## 6. memory_outside_window — label sumber: offend — LOLOS

Pemain: Galih, Rena, Surya, Mita

1. **Rena**: Galih tadi nuduh Surya, sekarang malah nuduh Mita  
   ↳ `offend` → Galih (offend)
2. **Surya**: iya, dia memang tidak konsisten dari tadi  
   ↳ `offend` → Galih (offend)
3. **Mita**: aku juga heran kenapa tiba-tiba aku yang dituduh  
   ↳ `defend` → Mita (defend)
4. **Rena**: orang yang tuduhannya berubah-ubah biasanya yang paling perlu dicurigai  
   ↳ `offend` → Galih (offend)
5. **Surya**: setuju, aku curiga dia sengaja mengalihkan perhatian  
   ↳ `offend` → Galih (offend)
6. **Mita**: kita perlu tanya langsung ke dia alasannya  
   ↳ `neutral` → -
7. **Galih**: aku punya alasan untuk keduanya, bukan asal tuduh  
   ↳ `defend` → Galih (defend)
8. **Rena**: alasan apa? tadi tidak ada penjelasan sama sekali  
   ↳ `offend` → Galih (offend)
9. **Surya**: benar, dia hanya ganti tuduhan tanpa dasar  
   ↳ `offend` → Galih (offend)
10. **Mita**: aku masih menunggu penjelasannya  
   ↳ `neutral` → -
11. **Rena**: sudah terlalu banyak alasan yang berubah dari dia  
   ↳ `offend` → Galih (offend)
12. **Surya**: aku tetap curiga, pola ini tidak wajar  
   ↳ `offend` → Galih (offend)
13. **Mita**: aku juga mulai ragu dengan penjelasannya  
   ↳ `offend` → Galih (offend)
**>>** **Rena**: orang yang terus ganti tuduhan seperti ini harus di-vote sekarang  
   ↳ `offend` → Galih (offend)

## 7. outside_window_unknown — label sumber: defend — DITOLAK — Kasus ambigu harus bertarget tidak_diketahui.

Pemain: Hani, Bram, Yosi, Deni

1. **Hani**: oke kita mulai dari awal lagi  
   ↳ `neutral` → -
2. **Bram**: siapa yang mau buka informasi?  
   ↳ `neutral` → -
3. **Yosi**: aku tidak punya info baru sekarang  
   ↳ `neutral` → -
4. **Deni**: sama, aku juga belum dapat apa-apa  
   ↳ `neutral` → -
5. **Hani**: baik, kita diskusi dari yang paling mencurigakan  
   ↳ `neutral` → -
6. **Bram**: menurutku belum ada yang terlalu menonjol  
   ↳ `neutral` → -
7. **Yosi**: iya, masih terlalu awal untuk menyimpulkan  
   ↳ `neutral` → -
8. **Deni**: kita tunggu saja perkembangan diskusi  
   ↳ `neutral` → -
9. **Hani**: ada yang mau klaim role sekarang?  
   ↳ `neutral` → -
10. **Bram**: aku Civilian, tidak ada klaim khusus  
   ↳ `neutral` → -
11. **Yosi**: aku juga tidak ada klaim  
   ↳ `neutral` → -
12. **Deni**: sama  
   ↳ `neutral` → -
13. **Hani**: chat tadi sepertinya terpotong, aku tidak sempat baca semuanya  
   ↳ `neutral` → -
**>>** **Bram**: aku tidak tahu maksud kamu, tapi aku bukan Hitman  
   ↳ `defend` → Bram (defend), tidak_diketahui (defend)

## 8. interruption — label sumber: offend — LOLOS

Pemain: Riko, Sela, Anto, Vera

1. **Sela**: Riko kemana semalam? tidak ada yang lihat dia  
   ↳ `offend` → Riko (offend)
2. **Anto**: iya, alibinya tidak jelas  
   ↳ `offend` → Riko (offend)
3. **Vera**: eh sebentar, ronde ini sudah hampir habis ya?  
   ↳ `neutral` → -
4. **Anto**: masih ada waktu, lanjut dulu  
   ↳ `neutral` → -
5. **Sela**: kembali ke tadi, Riko tidak bisa jelaskan aktivitasnya  
   ↳ `offend` → Riko (offend)
6. **Vera**: benar, alibi yang tidak jelas itu mencurigakan  
   ↳ `offend` → Riko (offend)
7. **Riko**: aku ada di area tengah semalam, bisa tanya ke Vera  
   ↳ `defend` → Riko (defend)
8. **Sela**: Vera juga tidak konfirmasi itu tadi  
   ↳ `offend` → Riko (offend)
**>>** **Anto**: alibi yang bergantung pada orang lain tanpa konfirmasi tetap mencurigakan, aku vote Riko  
   ↳ `offend` → Riko (offend)

## 9. topic_switch — label sumber: defend — LOLOS

Pemain: Nisa, Bayu, Tara, Egi

1. **Nisa**: Bayu kemarin vote ke Egi tanpa alasan jelas  
   ↳ `offend` → Bayu (offend)
2. **Bayu**: aku punya alasan, hanya tidak sempat jelaskan  
   ↳ `defend` → Bayu (defend)
3. **Egi**: oke lupakan itu dulu, sekarang kita bahas Tara yang pindah vote di detik terakhir  
   ↳ `offend` → Tara (offend)
4. **Nisa**: iya, perpindahan vote Tara itu memang aneh  
   ↳ `offend` → Tara (offend)
5. **Bayu**: aku juga heran dengan itu  
   ↳ `offend` → Tara (offend)
6. **Tara**: aku pindah vote karena dapat informasi baru, bukan karena mencurigakan  
   ↳ `defend` → Tara (defend)
7. **Egi**: informasi apa? kamu tidak bilang apa-apa sebelumnya  
   ↳ `offend` → Tara (offend)
**>>** **Tara**: aku tidak bisa ungkap sekarang, tapi vote aku bukan asal pindah  
   ↳ `defend` → Tara (defend)

## 10. ambiguous — label sumber: offend — DITOLAK — Intent pesan utama harus sesuai sumber.

Pemain: Fani, Rudi, Lena, Oka

1. **Fani**: Gag Order membuat banyak orang tidak bisa bicara tadi  
   ↳ `neutral` → -
2. **Rudi**: iya, aku juga kena efeknya  
   ↳ `neutral` → -
3. **Lena**: siapa yang kena Gag Order? ada yang tahu?  
   ↳ `neutral` → -
4. **Oka**: aku tidak tahu persis siapa yang kena  
   ↳ `neutral` → -
5. **Fani**: yang jelas efeknya terasa di diskusi tadi  
   ↳ `neutral` → -
6. **Rudi**: beberapa orang memang diam tidak wajar  
   ↳ `neutral` → -
7. **Lena**: diam krna Gag Order beda dengan diam karena sembunyi  
   ↳ `neutral` → -
8. **Oka**: tapi kita tidak bisa bedakan mana yang mana  
   ↳ `neutral` → -
9. **Fani**: betul, jadi sulit menilai siapa yang benar-benar mencurigakan  
   ↳ `neutral` → -
10. **Rudi**: aku curiga ada yang sengaja pakai Gag Order sebagai alasan untuk diam  
   ↳ `offend` → tidak_diketahui (offend)
**>>** **Lena**: siapa yang kamu maksud?  
   ↳ `neutral` → -

## 11. self — label sumber: defend — LOLOS

Pemain: Dara, Heru, Sinta, Bagas

1. **Heru**: Dara tadi bilang tidak tahu apa-apa, tapi sekarang tiba-tiba punya informasi  
   ↳ `offend` → Dara (offend)
2. **Sinta**: iya, ucapannya bertentangan  
   ↳ `offend` → Dara (offend)
3. **Bagas**: mungkin dia baru ingat sesuatu?  
   ↳ `defend` → Dara (defend)
4. **Heru**: baru ingat atau sengaja sembunyikan dari tadi?  
   ↳ `offend` → Dara (offend)
5. **Sinta**: aku juga curiga, pola seperti ini tidak wajar  
   ↳ `offend` → Dara (offend)
6. **Bagas**: kita dengarkan penjelasannya dulu  
   ↳ `neutral` → -
7. **Heru**: baik, tapi aku tetap curiga  
   ↳ `offend` → Dara (offend)
8. **Sinta**: aku juga masih ragu  
   ↳ `offend` → Dara (offend)
9. **Bagas**: beri dia kesempatan bicara dulu  
   ↳ `neutral` → -
**>>** **Dara**: aku tidak berbohong, informasi itu baru aku dapat tadi dan langsung aku sampaikan  
   ↳ `defend` → Dara (defend)

## 12. witness — label sumber: offend — DITOLAK — Pesan dengan relasi offend harus berintent offend.

Pemain: Wira, Nela, Ardi, Susi

1. **Wira**: ada yang mau klaim Stalker?  
   ↳ `neutral` → -
2. **Nela**: aku Stalker, sudah Peek ke Ardi semalam  
   ↳ `neutral` → -
3. **Ardi**: apa yang kamu lihat?  
   ↳ `neutral` → -
4. **Nela**: aku lihat Ardi bergerak ke arah Susi  
   ↳ `neutral` → -
5. **Wira**: itu mencurigakan, Susi kan korban malam ini  
   ↳ `offend` → Ardi (offend)
6. **Ardi**: aku tidak ke arah Susi, klaim Nela tidak akurat  
   ↳ `defend` → Ardi (defend), Nela (offend)
7. **Wira**: tapi Nela klaim Stalker, harusnya bisa lihat pergerakan  
   ↳ `offend` → Ardi (offend)
8. **Nela**: aku yakin dengan apa yang aku lihat, sdh Peek dengan benar  
   ↳ `offend` → Ardi (offend)
9. **Susi**: aku tidak tahu siapa yang ke arahku semalam  
   ↳ `neutral` → -
10. **Wira**: Susi tidak bisa konfirmasi, tapi klaim Nela tetap valid  
   ↳ `offend` → Ardi (offend)
11. **Ardi**: klaim Stalker tanpa bukti tambahan tidak cukup untuk vote aku  
   ↳ `defend` → Ardi (defend)
12. **Wira**: kita punya klaim Stalker yang jelas, itu sudah cukup  
   ↳ `offend` → Ardi (offend)
**>>** **Ardi**: klaim Stalker saja tidak otomatis benar, aku tetap tidak ke arah Susi malam itu  
   ↳ `defend` → Ardi (defend)

## 13. multiple_targets — label sumber: defend — LOLOS

Pemain: Rafi, Dian, Yuda, Mega

1. **Rafi**: Dian dan Yuda diam terus dari tadi, tidak ada kontribusi sama sekali  
   ↳ `offend` → Dian (offend), Yuda (offend)
**>>** **Mega**: aku tidak setuju, diam bukan berarti mencurigakan, mereka berdua mungkin sedang mengamati  
   ↳ `defend` → Dian (defend), Yuda (defend)

## 14. mixed_relations — label sumber: offend — LOLOS

Pemain: Toni, Resa, Gilang, Wati

1. **Resa**: Gilang langsung bela diri sebelum ada yang nuduh, itu mencurigakan  
   ↳ `offend` → Gilang (offend)
**>>** **Toni**: Gilang tidak mencurigakan, justru Wati yang terlalu cepat bela dia tanpa alasan  
   ↳ `offend` → Gilang (defend), Wati (offend)

## 15. quotation — label sumber: neutral — LOLOS

Pemain: Lia, Beni, Ciko

1. **Beni**: Ciko bilang tadi 'aku yakin Lia yang Hitman'  
   ↳ `offend` → Lia (offend)
**>>** **Lia**: Ciko memang bilang begitu, tapi aku tidak setuju dengan ucapannya itu  
   ↳ `neutral` → -

## 16. negation — label sumber: defend — LOLOS

Pemain: Hasan, Rini, Dodi, Fira

1. **Rini**: Hasan tadi nuduh Dodi, sekarang malah bilang Dodi tidak bersalah  
   ↳ `neutral` → -
2. **Dodi**: iya, tuduhannya berubah-ubah terus  
   ↳ `offend` → Hasan (offend)
3. **Fira**: Hasan memang tidak konsisten dari tadi  
   ↳ `offend` → Hasan (offend)
4. **Hasan**: aku berubah pikiran karena dapat informasi baru, bukan karena tidak konsisten  
   ↳ `defend` → Hasan (defend)
5. **Rini**: informasi apa? kamu tidak jelaskan apa-apa  
   ↳ `offend` → Hasan (offend)
6. **Dodi**: aku juga tidak terima dituduh tanpa dasar tadi  
   ↳ `defend` → Dodi (defend)
**>>** **Hasan**: aku tidak bilang Dodi bersalah sekarang, aku sudah ralat tuduhan itu  
   ↳ `defend` → Hasan (defend), Dodi (defend)

## 17. second_person — label sumber: offend — DITOLAK — Tidak ada jejak identitas pada teks atau memori yang dirujuk.

Pemain: Aldi, Nora

1. **Aldi**: chat kamu tadi terpotong, aku tidak baca semuanya  
   ↳ `neutral` → -
**>>** **Nora**: kamu sengaja diam waktu diskusi penting, itu mencurigakan  
   ↳ `offend` → Aldi (offend)

## 18. first_message — label sumber: neutral — LOLOS

Pemain: Seno, Tika, Ulum, Prita

**>>** **Seno**: Tika dan Ulum dari tadi tidak bicara sama sekali, itu mencurigakan  
   ↳ `neutral` → -

## 19. first_message_unknown — label sumber: defend — LOLOS

Pemain: Yanto

**>>** **Yanto**: dia kena Gag Order jadi tidak bisa bicara, itu bukan salahnya  
   ↳ `defend` → tidak_diketahui (defend)

## 20. first_message_self — label sumber: offend — LOLOS

Pemain: Reza

**>>** **Reza**: chat aku tadi terlambat masuk, jadi kelihatan seperti aku tidak respon  
   ↳ `offend` → Reza (offend)

## 21. short_history_1 — label sumber: neutral — LOLOS

Pemain: Iman, Sari

1. **Iman**: ada yang klaim Spy di sini?  
   ↳ `neutral` → -
**>>** **Sari**: aku belum dengar ada yang klaim Spy secara resmi  
   ↳ `neutral` → -

## 22. short_history_2 — label sumber: neutral — LOLOS

Pemain: Bowo, Lani, Rudi

1. **Bowo**: semalam aku di area selatan, tidak kemana-mana  
   ↳ `neutral` → -
2. **Lani**: aku juga tidak ada pergerakan mencurigakan dari tempatku  
   ↳ `neutral` → -
**>>** **Rudi**: baik, kita catat alibi masing-masing dulu sebelum diskusi lebih jauh  
   ↳ `neutral` → -

## 23. short_history_3 — label sumber: neutral — LOLOS

Pemain: Eko, Mira, Tono, Yuli

1. **Eko**: ada yang klaim Spy? aku belum dengar ada yang angkat tangan  
   ↳ `neutral` → -
2. **Mira**: aku bukan Spy, hanya Civilian biasa  
   ↳ `neutral` → -
3. **Tono**: aku juga tidak ada klaim khusus  
   ↳ `neutral` → -
**>>** **Yuli**: kalau memang ada Spy di sini, harusnya sudah klaim dari tadi  
   ↳ `neutral` → -

## 24. neutral_names — label sumber: neutral — LOLOS

Pemain: Hilda, Roni, Sandi, Tuti

1. **Hilda**: siapa yang berubah tuduhan dari ronde sebelumnya?  
   ↳ `neutral` → -
2. **Roni**: Sandi sempat nuduh Tuti, lalu ganti ke aku  
   ↳ `neutral` → -
3. **Sandi**: aku punya alasan untuk keduanya  
   ↳ `neutral` → -
4. **Tuti**: aku tidak masalah, asal ada dasar yang jelas  
   ↳ `neutral` → -
5. **Hilda**: kita catat semua perubahan tuduhan untuk referensi  
   ↳ `neutral` → -
6. **Roni**: baik, aku juga ingat Hilda sempat ragu-ragu di ronde dua  
   ↳ `neutral` → -
7. **Sandi**: iya, banyak yang berubah pikiran di tengah jalan  
   ↳ `neutral` → -
8. **Tuti**: itu wajar kalau dapat informasi baru  
   ↳ `neutral` → -
9. **Hilda**: yang penting ada alasan yang bisa dijelaskan  
   ↳ `neutral` → -
10. **Roni**: setuju, perubahan tanpa alasan yang mencurigakan  
   ↳ `neutral` → -
11. **Sandi**: kita rekap semua perubahan vote dari awal saja  
   ↳ `neutral` → -
12. **Tuti**: oke, aku catat dari ronde pertama  
   ↳ `neutral` → -
**>>** **Hilda**: Roni, Sandi, dan Tuti semua pernah ganti tuduhan, kita bahas satu per satu  
   ↳ `neutral` → -

## 25. neutral_after_accusation — label sumber: neutral — LOLOS

Pemain: Wendi, Ayu

1. **Wendi**: Ayu mencurigakan, aku curiga dia Hitman  
   ↳ `offend` → Ayu (offend)
**>>** **Ayu**: efek Gag Order memang membuat diskusi jadi tidak lancar ronde ini  
   ↳ `neutral` → -

## 26. neutral_status — label sumber: neutral — LOLOS

Pemain: Dimas, Rara, Joni

1. **Dimas**: chat aku tadi terlambat masuk karena koneksi  
   ↳ `neutral` → -
2. **Rara**: aku juga sempat tidak bisa kirim pesan tadi  
   ↳ `neutral` → -
**>>** **Joni**: aku Guard, tidak ada klaim khusus selain itu  
   ↳ `neutral` → -

## 27. agreement — label sumber: defend — LOLOS

Pemain: Feri, Gina, Hadi, Ika

1. **Feri**: Hadi vote ke kiri terus tanpa alasan jelas  
   ↳ `offend` → Hadi (offend)
2. **Gina**: aku tidak setuju, Hadi punya pola yang bisa dijelaskan  
   ↳ `defend` → Hadi (defend)
3. **Ika**: aku setuju dengan Gina, pola vote Hadi tidak mencurigakan  
   ↳ `defend` → Hadi (defend)
4. **Feri**: kalian terlalu cepat membela tanpa bukti  
   ↳ `offend` → Hadi (offend)
5. **Gina**: buktinya ada, kamu yang tidak mau lihat  
   ↳ `defend` → Hadi (defend)
**>>** **Hadi**: aku tidak perlu dibela, vote aku memang punya dasar yang jelas  
   ↳ `defend` → Hadi (defend)

## 28. plural_reference — label sumber: offend — LOLOS

Pemain: Soni, Reni, Aldo, Mela

1. **Soni**: Reni dan Aldo langsung bela diri sebelum ada yang nuduh mereka  
   ↳ `offend` → Reni (offend), Aldo (offend)
2. **Mela**: iya, itu memang mencurigakan  
   ↳ `offend` → Reni (offend), Aldo (offend)
3. **Soni**: keduanya jg tidak kasih alasan yang masuk akal  
   ↳ `offend` → Reni (offend), Aldo (offend)
**>>** **Mela**: kita vote mereka berdua saja sekarang  
   ↳ `offend` → Reni (offend), Aldo (offend)

## 29. rhetorical_question — label sumber: defend — LOLOS

Pemain: Niko, Rani, Budi, Sinta

1. **Rani**: Niko klaim Stalker tapi hasilnya tidak masuk akal  
   ↳ `offend` → Niko (offend)
2. **Budi**: iya, Peek ke arah itu tidak mungkin dilakukan Stalker  
   ↳ `offend` → Niko (offend)
3. **Sinta**: aku ragu juga, klaimnya terlalu dipaksakan  
   ↳ `offend` → Niko (offend)
4. **Niko**: klaim aku valid, kalian yang salah baca situasinya  
   ↳ `defend` → Niko (defend)
5. **Rani**: valid bagaimana? detail yang kamu kasih tidak konsisten  
   ↳ `offend` → Niko (offend)
6. **Budi**: aku tetap curiga, penjelasannya tidak memuaskan  
   ↳ `offend` → Niko (offend)
7. **Sinta**: kita tanya lebih detail dulu sebelum vote  
   ↳ `neutral` → -
8. **Rani**: baik, tapi aku masih ragu  
   ↳ `offend` → Niko (offend)
**>>** **Budi**: masa sih Niko benar-benar Stalker? hasil Peek itu tidak masuk akal sama sekali  
   ↳ `defend` → Niko (defend)

## 30. nickname — label sumber: neutral — LOLOS

Pemain: Andika, Rosi, Tegar, Wulan | Panggilan: [{'pemain': 'Andika', 'sebutan': ['Andi', 'Dika']}]

1. **Rosi**: siapa yang berubah tuduhan dari ronde sebelumnya?  
   ↳ `neutral` → -
2. **Tegar**: Andika sempat nuduh Wulan, lalu ganti ke Rosi  
   ↳ `neutral` → -
3. **Wulan**: iya, aku ingat itu  
   ↳ `neutral` → -
4. **Rosi**: perubahan itu mencurigakan  
   ↳ `offend` → Andika (offend)
5. **Tegar**: mungkin dia dapat informasi baru  
   ↳ `defend` → Andika (defend)
6. **Wulan**: kita tanya langsung saja ke dia  
   ↳ `neutral` → -
7. **Andika**: aku punya alasan untuk perubahan itu  
   ↳ `defend` → Andika (defend)
8. **Rosi**: alasan apa? tidak ada yang tahu  
   ↳ `offend` → Andika (offend)
9. **Tegar**: beri dia kesempatan jelaskan  
   ↳ `defend` → Andika (defend)
10. **Wulan**: aku tunggu penjelasannya  
   ↳ `neutral` → -
11. **Rosi**: sudah terlalu lama menunggu penjelasan dari dia  
   ↳ `offend` → Andika (offend)
**>>** **Tegar**: Andi memang belum kasih penjelasan yang memuaskan, tapi aku belum mau vote dia sekarang  
   ↳ `neutral` → -

## 31. stance_change — label sumber: offend — DITOLAK — Intent pesan utama harus sesuai sumber.

Pemain: Raka, Sela, Tomi

1. **Raka**: Sela dari tadi diam terus, itu mencurigakan  
   ↳ `offend` → Sela (offend)
2. **Tomi**: aku setuju, pemain pasif perlu dipertanyakan  
   ↳ `offend` → Sela (offend)
**>>** **Raka**: sebenarnya aku salah tadi, Sela sudah bicara beberapa kali, aku yang tidak perhatikan  
   ↳ `defend` → Sela (defend)

## 32. ambiguous — label sumber: defend — LOLOS

Pemain: Fani, Geri, Hana, Iko

1. **Fani**: ada yang terlalu cepat bela diri tadi  
   ↳ `offend` → tidak_diketahui (offend)
2. **Geri**: siapa yg kamu maksud?  
   ↳ `neutral` → -
3. **Fani**: yang langsung angkat bicara sebelum ada tuduhan  
   ↳ `offend` → tidak_diketahui (offend)
4. **Hana**: aku tidak merasa melakukan itu  
   ↳ `defend` → Hana (defend)
5. **Iko**: aku juga tidak  
   ↳ `defend` → Iko (defend)
6. **Geri**: mungkin Fani salah ingat  
   ↳ `defend` → tidak_diketahui (defend)
7. **Fani**: aku tidak salah ingat, aku perhatikan dari tadi  
   ↳ `offend` → tidak_diketahui (offend)
8. **Hana**: kalau memang ada, sebutkan siapa orangnya  
   ↳ `neutral` → -
9. **Iko**: iya, jangan hanya klaim tanpa nama  
   ↳ `neutral` → -
10. **Geri**: aku juga ingin tahu siapa yang dimaksud  
   ↳ `neutral` → -
11. **Fani**: aku masih mengamati, belum mau sebut nama sekarang  
   ↳ `neutral` → -
12. **Hana**: kalau tidak mau sebut, kita tidak bisa diskusi lebih lanjut  
   ↳ `neutral` → -
**>>** **Iko**: aku tidak tahu siapa yang dimaksud Fani, tapi aku tidak melakukan pembelaan terlalu cepat  
   ↳ `defend` → tidak_diketahui (defend)

## 33. explicit — label sumber: defend — LOLOS

Pemain: Luki, Mona, Nino, Ola

1. **Luki**: chat Mona tadi terpotong, aku tidak baca semuanya  
   ↳ `neutral` → -
2. **Mona**: aku kirim ulang tapi tidak masuk  
   ↳ `neutral` → -
3. **Nino**: aku juga tidak baca pesan Mona yang tadi  
   ↳ `neutral` → -
**>>** **Ola**: Mona bukan Hitman, aku yakin itu  
   ↳ `defend` → Mona (defend)

## 34. first_message — label sumber: defend — LOLOS

Pemain: Bima, Rara, Seto

**>>** **Bima**: Rara dari tadi tidak bicara sama sekali, itu tidak wajar  
   ↳ `defend` → Rara (defend)

## 35. first_message_self — label sumber: defend — LOLOS

Pemain: Wawan

**>>** **Wawan**: aku bukan Hitman, identitas korban juga bukan urusanku  
   ↳ `defend` → Wawan (defend)

## 36. interruption — label sumber: defend — LOLOS

Pemain: Nana, Oki, Pita, Qori

1. **Nana**: Oki klaim Stalker tapi hasilnya tidak konsisten  
   ↳ `offend` → Oki (offend)
2. **Pita**: iya, Peek yang dia klaim tidak masuk akal  
   ↳ `offend` → Oki (offend)
3. **Qori**: sebentar, timer hampir habis ya?  
   ↳ `neutral` → -
4. **Nana**: masih ada waktu, lanjut bahas Oki dulu  
   ↳ `neutral` → -
5. **Pita**: kembali ke tadi, klaim Stalker Oki perlu dipertanyakan  
   ↳ `offend` → Oki (offend)
6. **Qori**: aku setuju, hasilnya tidak masuk akal  
   ↳ `offend` → Oki (offend)
7. **Oki**: klaim aku valid, Peek itu memang yang aku lihat  
   ↳ `defend` → Oki (defend)
**>>** **Nana**: kalau valid, kenapa hasilnya tidak konsisten dengan situasi malam itu?  
   ↳ `defend` → Oki (defend)

## 37. memory_outside_window — label sumber: defend — LOLOS

Pemain: Andi, Bela, Ciko, Doni

1. **Bela**: Andi pindah vote terus dari ronde ke ronde  
   ↳ `offend` → Andi (offend)
2. **Ciko**: iya, pola votenya tidak jelas  
   ↳ `offend` → Andi (offend)
3. **Doni**: kita tanya alasannya dulu  
   ↳ `neutral` → -
4. **Bela**: sudah ditanya tapi tidak ada jawaban yang memuaskan  
   ↳ `offend` → Andi (offend)
5. **Ciko**: aku tetap curiga dengan pola votenya  
   ↳ `offend` → Andi (offend)
6. **Doni**: beri dia kesempatan jelaskan dulu  
   ↳ `defend` → Andi (defend)
7. **Bela**: sudah terlalu lama menunggu penjelasan  
   ↳ `offend` → Andi (offend)
8. **Ciko**: aku setuju, kita tidak bisa terus menunggu  
   ↳ `offend` → Andi (offend)
9. **Doni**: oke, aku mulai ragu juga sekarang  
   ↳ `offend` → Andi (offend)
10. **Bela**: pola vote yang tidak konsisten itu tanda yang jelas  
   ↳ `offend` → Andi (offend)
11. **Ciko**: aku setuju, sudah cukup bukti  
   ↳ `offend` → Andi (offend)
12. **Doni**: dia memang tidak bisa jelaskan pola votenya dari tadi  
   ↳ `offend` → Andi (offend)
13. **Bela**: aku masih ingat dari awal, pola itu tidak wajar  
   ↳ `offend` → Andi (offend)
**>>** **Ciko**: aku tidak setuju dia di-vote, pola vote bisa berubah karena informasi baru  
   ↳ `defend` → Andi (defend)

## 38. nickname — label sumber: defend — DITOLAK — Panggilan 'Rizal' untuk Rizal tidak valid atau ambigu.

Pemain: Rizal, Sinta, Tono | Panggilan: [{'pemain': 'Rizal', 'sebutan': ['Zal', 'Rizal']}]

1. **Sinta**: Rizal semalam ada di mana?  
   ↳ `neutral` → -
2. **Tono**: aku lihat dia di area utara  
   ↳ `neutral` → -
**>>** **Sinta**: Zal, alibi kamu di area utara itu bisa dikonfirmasi tidak?  
   ↳ `neutral` → -

## 39. plural_reference — label sumber: defend — DITOLAK — Tidak ada jejak identitas pada teks atau memori yang dirujuk.

Pemain: Heri, Ina, Joko, Kiki

1. **Heri**: Ina dan Joko bilang mereka tidak tahu identitas korban  
   ↳ `neutral` → -
2. **Kiki**: aku juga tidak tahu, identitas korban memang tidak diumumkan  
   ↳ `neutral` → -
3. **Heri**: tapi ada yang bilang mereka berdua terlihat di dekat lokasi kejadian  
   ↳ `offend` → Ina (offend), Joko (offend)
4. **Kiki**: itu tidak cukup untuk menuduh, keduanya sudah bilang tidak tahu apa-apa  
   ↳ `defend` → Ina (defend), Joko (defend)
5. **Heri**: dekat lokasi kejadian tetap mencurigakan  
   ↳ `offend` → Ina (offend), Joko (offend)
6. **Ina**: aku dan Joko memang ada di sana, tapi bukan berarti kami tahu identitas korban  
   ↳ `defend` → Ina (defend), Joko (defend)
**>>** **Kiki**: mereka berdua sudah jelaskan, itu cukup masuk akal  
   ↳ `defend` → Ina (defend), Joko (defend)

## 40. quotation — label sumber: defend — DITOLAK — Kasus kutipan perlu kutipan atau kata pelapor.

Pemain: Aldi, Bina, Ciko

1. **Bina**: chat Aldi tadi terpotong, aku tidak baca semuanya  
   ↳ `neutral` → -
2. **Ciko**: Aldi tadi bilang 'aku bukan Hitman' tapi chatnya tidak masuk semua  
   ↳ `neutral` → -
**>>** **Aldi**: Ciko benar mengutip itu, tapi aku memang tidak bohong soal itu  
   ↳ `defend` → Aldi (defend)

## 41. reference_middle — label sumber: defend — LOLOS

Pemain: Rani, Seno, Tara, Udi

1. **Rani**: diskusi dimulai, ada yang mau buka informasi?  
   ↳ `neutral` → -
2. **Tara**: aku tidak punya info khusus malam ini  
   ↳ `neutral` → -
3. **Udi**: sama, aku juga tidak ada klaim  
   ↳ `neutral` → -
4. **Rani**: baik, kita lihat dari pola diskusi saja  
   ↳ `neutral` → -
5. **Tara**: belum ada yang terlalu menonjol sejauh ini  
   ↳ `neutral` → -
6. **Udi**: Seno berubah tuduhan dari ronde sebelumnya, itu mencurigakan  
   ↳ `offend` → Seno (offend)
7. **Rani**: iya, aku juga perhatikan itu  
   ↳ `offend` → Seno (offend)
8. **Tara**: mungkin dia dapat informasi baru  
   ↳ `defend` → Seno (defend)
9. **Udi**: informasi apa? tidak ada yang tahu  
   ↳ `offend` → Seno (offend)
10. **Rani**: kita tanya langsung ke dia  
   ↳ `neutral` → -
11. **Tara**: setuju, beri dia kesempatan jelaskan  
   ↳ `neutral` → -
12. **Udi**: aku tunggu penjelasannya  
   ↳ `neutral` → -
**>>** **Seno**: aku tidak asal ganti tuduhan, ada alasan yang bisa aku jelaskan  
   ↳ `defend` → Seno (defend)

## 42. second_person — label sumber: defend — DITOLAK — Intent pesan utama harus sesuai sumber.

Pemain: Aldo, Beni, Cika, Dara

1. **Aldo**: chat tadi terpotong, aku tidak baca semua  
   ↳ `neutral` → -
2. **Beni**: aku juga tidak sempat baca semuanya  
   ↳ `neutral` → -
3. **Cika**: ada yang bisa rekap isi chat yang terpotong?  
   ↳ `neutral` → -
4. **Dara**: aku tidak ingat persis isinya  
   ↳ `neutral` → -
5. **Aldo**: kamu bilang sesuatu sebelum chat terpotong, apa itu?  
   ↳ `neutral` → -
**>>** **Beni**: aku tidak tahu kamu tanya ke siapa  
   ↳ `neutral` → -

## 43. short_history_1 — label sumber: defend — DITOLAK — Target tidak diketahui tidak boleh punya bukti identitas pasti.

Pemain: Hendra, Lina

1. **Hendra**: vote ke Lina tanpa bukti itu tidak adil  
   ↳ `offend` → tidak_diketahui (offend)
**>>** **Lina**: aku setuju, tidak ada bukti yang cukup untuk vote aku sekarang  
   ↳ `defend` → Lina (defend)

## 44. short_history_2 — label sumber: defend — LOLOS

Pemain: Rina, Sandi, Tomi

1. **Rina**: Sandi dari tadi tidak bicara sama sekali  
   ↳ `offend` → Sandi (offend)
2. **Tomi**: iya, pemain pasif memang mencurigakan  
   ↳ `offend` → Sandi (offend)
**>>** **Sandi**: aku tidak pasif, aku hanya mengamati dulu sebelum bicara  
   ↳ `defend` → Sandi (defend)

## 45. short_history_3 — label sumber: defend — DITOLAK — Intent pesan utama harus sesuai sumber.

Pemain: Eko, Fani, Gita, Heru

1. **Eko**: ada yang klaim Spy? aku belum dengar ada yang angkat tangan  
   ↳ `neutral` → -
2. **Fani**: aku tidak klaim apa-apa, hanya Civilian  
   ↳ `neutral` → -
3. **Gita**: aku juga tidak ada klaim khusus  
   ↳ `neutral` → -
**>>** **Heru**: kalau memang ada Spy, klaim sekarang sebelum terlambat  
   ↳ `neutral` → -

## 46. stance_change — label sumber: defend — LOLOS

Pemain: Aldi, Bela, Ciko, Dara

1. **Aldi**: Bela dari tadi tidak bicara, itu mencurigakan  
   ↳ `offend` → Bela (offend)
2. **Ciko**: iya, pemain pasif perlu dipertanyakan  
   ↳ `offend` → Bela (offend)
3. **Dara**: mungkin dia sedang mengamati saja  
   ↳ `defend` → Bela (defend)
4. **Aldi**: mengamati atau menyembunyikan sesuatu?  
   ↳ `offend` → Bela (offend)
5. **Ciko**: aku tetap curiga  
   ↳ `offend` → Bela (offend)
6. **Dara**: kita tanya langsung ke dia dulu  
   ↳ `neutral` → -
7. **Bela**: aku memang mengamati, itu cara aku bermain  
   ↳ `defend` → Bela (defend)
8. **Aldi**: oke, aku terima penjelasan itu, Bela tidak mencurigakan  
   ↳ `defend` → Bela (defend)
**>>** **Ciko**: aku masih ragu, tapi aku tidak akan vote dia sekarang  
   ↳ `defend` → Bela (defend)

## 47. witness — label sumber: defend — DITOLAK — Tidak ada jejak identitas pada teks atau memori yang dirujuk.

Pemain: Rani, Soni, Tika, Udi

1. **Rani**: ada yang klaim Spy di sini?  
   ↳ `neutral` → -
2. **Soni**: aku klaim Spy, sudah amati beberapa pemain  
   ↳ `neutral` → -
3. **Tika**: klaim Spy tanpa bukti tidak bisa langsung dipercaya  
   ↳ `offend` → Soni (offend)
4. **Udi**: iya, klaim saja tidak cukup  
   ↳ `offend` → Soni (offend)
5. **Rani**: Tika juga pernah klaim Spy di ronde sebelumnya tanpa bukti  
   ↳ `offend` → Tika (offend)
6. **Soni**: aku punya informasi yang bisa aku bagikan, tapi perlu waktu  
   ↳ `neutral` → -
7. **Tika**: informasi apa? kamu tidak bilang apa-apa dari tadi  
   ↳ `offend` → Soni (offend)
**>>** **Udi**: aku tidak percaya klaim Spy Soni, tapi aku juga tidak langsung vote dia  
   ↳ `defend` → Soni (defend)

## 48. original — label sumber: neutral — LOLOS

Pemain: Player1

Teks sumber asli: _sumpah kaget pas layar berubah ke fase pagi_

**>>** **Player1**: sumpah kaget pas layar berubah ke fase pagi  
   ↳ `neutral` → -

## 49. agreement — label sumber: offend — LOLOS

Pemain: Aldi, Beni, Cika, Doni

1. **Beni**: Aldi bilang tidak tahu apa-apa, tapi tadi dia bilang hal yang berbeda  
   ↳ `offend` → Aldi (offend)
2. **Cika**: iya, ucapannya bertentangan  
   ↳ `offend` → Aldi (offend)
3. **Doni**: mungkin dia salah ingat saja  
   ↳ `defend` → Aldi (defend)
4. **Beni**: salah ingat atau sengaja sembunyikan?  
   ↳ `offend` → Aldi (offend)
5. **Cika**: aku curiga dia sengaja  
   ↳ `offend` → Aldi (offend)
6. **Doni**: kita tanya langsung ke dia dulu  
   ↳ `neutral` → -
7. **Aldi**: aku tidak berbohong, aku jelaskan nanti  
   ↳ `defend` → Aldi (defend)
8. **Beni**: sudah terlalu banyak kontradiksi dari dia  
   ↳ `offend` → Aldi (offend)
9. **Cika**: aku setuju dengan Beni  
   ↳ `offend` → Aldi (offend)
**>>** **Doni**: aku juga setuju, terlalu banyak kontradiksi  
   ↳ `offend` → Aldi (offend)

## 50. first_message — label sumber: offend — DITOLAK — Pembuka dengan target ambigu masuk kasus first_message_unknown.

Pemain: Roni

**>>** **Roni**: aku curiga ada yang terlalu cepat bela diri sebelum diskusi dimulai  
   ↳ `offend` → tidak_diketahui (offend)
