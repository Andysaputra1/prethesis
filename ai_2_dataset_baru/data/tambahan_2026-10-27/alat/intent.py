"""100 chat intent yang ditulis Codex beserta kategori audit terpisah dari CSV."""
import csv,json
from pathlib import Path
FOLDER=Path(__file__).resolve().parents[1]
GROUPS={
'peek_membersihkan':('defend','''
gw Stalker, peek barusan ke Sekar hasilnya Civilian kok
hasil pengintaian gw nunjukin si K bukan Hitman, tahan vote dulu
aku sudah Peek Kirana semalam, dia bersih dari hasil itu
catatan peek-ku: Niken aman, nggak ada hasil yang bilang dia pelaku
buat yang nanya hasil, Pram itu Civilian menurut Peek aku
Wening jangan diseret, di layar hasil Peek-ku tertulis bukan Hitman
aku dapat konfirmasi lewat Peek kalau Larasati warga biasa
bukan Hitman hasilnya untuk si R, itu yang keluar dari peek gw
habis cek Baskara pakai Peek, gw nggak nemu alasan vote dia: Civilian
hasil skill Stalker-ku membersihkan Cakra, jadi aku bela dia
si P aman dari peek tadi, bukan anggota pihak jahat yang kita cari
Prabu ternyata Civilian waktu kuintip semalam
aku stalker ya, dan hasilku ke Mahesa bilang dia bukan pelaku
Pandu aman kok, bukan nebak; itu bacaan dari hasil Peek-ku
peek gw kali ini nyebut Satya warga, jangan buang suara ke dia
aku sudah lihat role Yudhis lewat Peek, bukan Hitman
Aruna bersih di hasil pengecekanku, gw Stalker yang melakukan Peek itu
hasil peek semalam buat si L: Civilian, tolong catat pembelaan ini
yang kuintip Aksara dan hasilnya membebaskan dia dari tuduhan Hitman
Renata nggak jahat dari hasil Peek aku, jangan buru-buru eksekusi
cekanku ke Keisha pakai skill Stalker menunjukkan Civilian
gw dapet Nadira bukan Hitman dari Peek, jadi jangan curiga ke dia dulu
Naura warga biasa, itu hasil skill-ku semalam bukan kesan pribadi
aku Peek Salma, hasilnya bersih. Vote ke Salma sebaiknya ditahan
si Q bukan Hitman di hasil pengintaian gw, aman buat sekarang
Safira terbaca Civilian waktu aku menggunakan Peek tadi malam
hasil yang muncul setelah Peek ke Almira itu bukan Hitman
aku stalker dan mau luruskan: Anindya aman berdasarkan hasilku
Kinanti tidak masuk Hitman dari cek Peek semalam, aku bela dia
gw intip si T dan keterangannya warga biasa, bukan pelaku
Ajeng aman ya, layar Peek-ku nyebut Civilian dengan jelas
hasilku membersihkan Ayuning; semalam dia yang jadi target Peek aku
Rengga bukan Hitman menurut skill yang kupakai, gw Stalker
aku dapat Raksa sebagai warga lewat Peek, tuduhan itu meleset
si U terbaca bukan Hitman, itu laporan hasil Peek-ku ronde ini
Tirta jangan divote, aku mengintipnya dan hasilnya Civilian
peek ke Banyu selesai, hasilnya justru membela dia: bukan Hitman
aku punya hasil pengintaian buat Damar, dia aman dari tuduhan pelaku
Jalu Civilian dari hasil Stalker-ku, bukan orang jahat yang dicari
si W bersih kok, aku sendiri yang Peek dan melihat hasil bukan Hitman
Bagaskara ternyata bukan Hitman setelah kucek menggunakan Peek
gw melaporkan Wardana aman berdasarkan Peek, jangan salah vote
hasil Peek-ku ke Mahira menunjukkan warga biasa, jadi aku percaya dia
Khalisa bersih dari hasil skill-ku. Gw Stalker, bukan sekadar ikut membela
si Y hasilnya Civilian pas aku Peek, itu alasan aku nggak mau vote dia
Nadhif bukan pelaku menurut hasil pengintaian semalam
aku pakai Peek ke Haris, ternyata Civilian dan tidak layak dituduh Hitman
Syauqi aman dari cekanku, hasil Peek-nya bukan Hitman
gw intip Haikal semalam dan yang kebaca warga biasa, stop tuduh dia
untuk Zafran hasil Peek yang kudapat membersihkan dia, bukan Hitman
'''),
'klaim_pembelaan':('defend','''
gw Spy, jangan tuntut aku ngasih hasil Peek yang memang bukan skill gw
aku Civilian, jadi jangan vote aku cuma karena nggak punya laporan aksi malam
role-ku Stalker, tuduhan aku melakukan Hostage itu salah
kalian boleh meragukan, tapi aku Spy dan nggak melakukan Gag Order
aku bukan Hitman, aku warga biasa; itu sebabnya nggak ada skill buat kulaporkan
gw Stalker, jangan paksa gw ngaku ngelakuin aksi penyerangan
aku klaim Civilian dan menolak vote ke diriku, tuduhannya belum ada bukti
jangan asal buang aku, role-ku Spy dan kerjaanku Guard
aku memang Stalker, bukan pelaku yang kalian tuduhkan tadi
gw warga biasa, jangan suruh gw mengarang hasil skill biar dianggap aman
aku Spy, jadi tuduhan bahwa aku menyandera orang itu tidak benar
mau percaya atau nggak, aku Civilian; aku nggak bersalah di ronde ini
role gw Stalker, tolong jangan eksekusi gw dari dugaan semata
aku bukan Hitman kok, aku Spy dan siap menjelaskan aksi Guard-ku
klaimku Civilian, jangan jadikan tidak punya hasil Peek sebagai alasan vote aku
gw Stalker dan menolak tuduhan itu, aksi gw cuma Peek
aku Spy, jangan desak aku memberikan hasil pengintaian palsu
aku warga biasa, bukan yang menutup chat orang seperti tuduhan tadi
jangan paksa aku mengaku pelaku, aku Stalker dan role itu yang sebenarnya
aku Civilian, tuduhan melakukan aksi malam ke aku salah alamat
'''),
'peek_memberatkan':('offend','''
hasil Peek-ku ke Rasyid menunjukkan Hitman, aku curiga dia
gw Stalker, si Z kebaca Hitman waktu kuintip semalam
Ghani terdeteksi pelaku di hasil Peek aku, jangan percaya klaim warga itu
aku sudah cek Ghina dengan Peek, hasilnya Hitman
si M bukan aman, Peek gw justru bilang Hitman
Syifa Hitman dari laporan skill-ku semalam, arahkan vote ke dia
aku Stalker dan hasil pengintaian memberatkan Tsania: Hitman
peek ke Syakira keluar role Hitman, kita punya alasan vote sekarang
hasilku jelas buat si H, dia Hitman menurut Peek yang kulakukan
Aisyah terbaca Hitman di hasil Peek-ku, aku mau menuduh dia
gw intip Khansa dan hasilnya pelaku, dia Hitman
Fathia terindikasi Hitman dari Peek semalam, bukan cuma feeling gw
hasil Stalker-ku ke si J itu Hitman, hati-hati sama klaimnya
Afifah punya hasil Peek Hitman di catatanku, aku pilih vote dia
Atika bukan warga dari hasil lengkap Peek-ku: role-nya Hitman
'''),
'klaim_murni':('neutral','''
aku klaim Spy untuk dicatat di daftar role ronde ini
role gw Civilian, itu info yang mau kutulis dulu
aku Stalker, laporan Peek nanti kutaruh di pesan terpisah
klaimku warga biasa, silakan masukkan ke catatan grup
gw Spy dan semalam pakai Guard satu kali
untuk kolom role, isi namaku dengan klaim Stalker
aku menyatakan Civilian di pembahasan role sekarang
giliran aku ya, role yang kuklaim Spy
aku Stalker, belum ada tambahan keterangan untuk saat ini
gw warga biasa, cuma mau melengkapi daftar klaim
catat pengakuanku sebagai Spy, itu saja infonya
role-ku Stalker dan aku sudah menggunakan Peek malam kedua
aku mengaku Civilian pada ronde ini, biar catatannya lengkap
gw klaim Spy, nanti waktu penggunaan Guard kutulis lagi
aku Stalker; ini pesan klaim role sebelum masuk laporan hasil
'''),
}

def main():
    records=[]; manifest=[]
    for pattern,(label,text) in GROUPS.items():
        lines=text.strip().splitlines()
        for line in lines:
            records.append(dict(teks_chat=line.strip(),label_intent=label))
            manifest.append(dict(row=len(records)+1,pattern=pattern,teks_chat=line.strip(),label_intent=label))
    assert len(records)==100
    path=FOLDER.parent/'dataset_intent_tambahan.csv'
    with path.open('x',encoding='utf-8-sig',newline='') as h:
        writer=csv.DictWriter(h,fieldnames=['teks_chat','label_intent'],lineterminator='\r\n')
        writer.writeheader();writer.writerows(records)
    (FOLDER/'alat'/'intent_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    print('100 chat intent ditulis (70 defend, 15 offend, 15 neutral).')

if __name__=='__main__':main()
