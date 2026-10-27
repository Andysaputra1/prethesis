"""Revisi hanya teks; jawaban kemudian diimpor ulang dengan validator salinan."""
import copy,csv,json,random,re,sys
from pathlib import Path
R=Path(__file__).resolve().parent
F=R.parents[1]
sys.path.insert(0,str(R.parent))
import label_target as lt
from tulis_sesi import NAMES
from gaya_revisi1 import metrics
from riwayat_panjang import THREADS
from riwayat_pendek import PAIR,PAIR_REPLY,GROUP,TIMERS,ROLE,REQUEST,REPLY,WAIT,TIME_REPLY,lines

NAMED=lines('''
{a} sudah cerita soal malam tadi, bagian akhirnya baru masuk nih.
gw habis baca pengakuan {a}, ada keterangan waktunya juga.
{a} nulis role dulu lalu menjelaskan skill yang dimaksud.
yang mau bahas klaim {a}, pesannya masih di atas kok.
{a} baru menjawab pertanyaan grup tentang urutan malam.
aku dengar {a} menyebut waktu sebelum fase berganti.
{a} sudah selesai ngetik alasannya soal pilihan vote.
gw baru baca cerita {a} sampai nomor malamnya.
pesan dari {a} itu menyebut kapan hasil skill terlihat.
{a} menambah penjelasan setelah pengakuan role tadi.
aku sudah melihat jawaban {a} pada chat sebelumnya.
nih, {a} cerita aksi malamnya sebelum menulis pilihan vote.
{a} baru mengirim lanjutan setelah pesan pertama.
gw lihat {a} menjelaskan bagian waktunya di akhir kalimat.
{a} menyebut hasil skill di pesan yang barusan lewat.
aku membaca cerita {a} dari awal diskusi sih.
{a} sudah menjawab soal role, tinggal bahas isi jawabannya.
pesan {a} masih tentang malam yang baru selesai.
gw sempat baca pengantar klaim {a} sebelum hasilnya masuk.
{a} menyampaikan urutan kejadian dari sebelum chat terbuka.
aku lihat {a} menyebut nomor malam dengan jelas sekarang.
{a} menjelaskan apa yang ingin dilaporkan pada ronde ini.
yang baru mengirim cerita soal aksi itu {a}.
gw belum menanggapi, baru selesai baca pesan {a}.
{a} sudah menyebut skill dan waktu penggunaannya di chat.
''')
ACC=lines('''
{s}, gw curiga kamu Hitman, belum jawab dari tadi sih.
aku pilih vote {s}, diamnya kayak sedang menutup sesuatu.
klaim {s} kedengeran palsu, aku nggak percaya role itu.
{s} sus banget menurutku, jeda jawabnya terasa disengaja.
gw menduga {s} pelakunya, cerita aksinya belum meyakinkan.
{s}, alasanmu telat itu janggal, aku mau vote kamu.
jangan percaya {s}, klaimnya seperti alibi yang dibuat-buat.
yang gw curigai {s}, kok terus menghindari pertanyaan aksi?
aku mau {s} dikeluarkan, cara jawabnya seperti Hitman cari aman.
{s} pasti nutup sesuatu, aku nggak anggap diamnya kebetulan.
gw ragu sama {s}, alibinya berubah setelah kita tanya lagi.
{s} paling mencurigakan buatku, pengakuan role-nya terasa palsu.
aku vote {s} aja, penjelasan malamnya nggak nyambung.
{s}, kenapa cerita aksimu beda terus? Aku curiga kamu bohong.
gw nggak percaya pengakuan {s}, kedengarannya cuma buat lolos.
{s} itu sus, selalu nunggu arah vote baru memberi alasan.
aku menuduh {s} sebagai Hitman, klaim skillnya kelewat janggal.
pilihanku tetap vote {s}, ada bagian alibinya yang ngarang.
{s} kayak sengaja mengulur chat, aku curiga motifnya.
gw pikir {s} menyembunyikan hasil malam, itu bikin makin sus.
{s}, aku nggak beli klaim itu, role-mu kayak cuma tameng.
aku curiga {s} yang melakukan Hostage, alasannya belum cocok.
gw akan vote {s}, cara mengganti cerita itu mencurigakan.
{s} bohong soal waktu aksinya menurutku, jangan dipercaya dulu.
aku menandai {s} sebagai calon pelaku, pengakuannya terlalu janggal.
''')
PEEK_ACC=lines('''
Peek gw ke {s} keluar Hitman, aku curiga dia.
{s} Hitman dari hasil Peek-ku semalam, itu yang terlihat nih.
gw sudah intip {s}, hasilnya justru Hitman.
hasil Stalker-ku bilang {s} Hitman, bukan Civilian.
aku Peek {s} dan dapat Hitman, makanya aku tuduh dia.
{s} terdeteksi Hitman di hasil skill Peek yang kupakai.
di hasil Peek-ku ada role Hitman buat {s}, aku mau vote dia.
gw Stalker, {s} yang kuintip tadi hasilnya Hitman.
laporan Peek-ku memberatkan {s}, role-nya Hitman.
aku dapat hasil Hitman waktu Peek {s} malam kedua.
{s} bukan aman dari hasilku, Peek-ku menyebut Hitman kok.
gw mau lapor hasil Peek {s}: Hitman, jadi aku curiga.
''')
AGREE_D=lines('''
{a} bukan Hitman menurutku, jangan buru-buru buang dia.
hasil Peek-ku ke {a} Civilian, jadi jangan vote dia dong.
tuduhan ke {a} belum ada bukti, aku nggak ikut vote itu.
{a} aman kok, keterlambatan chatnya masih bisa dijelaskan.
gw percaya {a} warga, diam sebentar belum berarti pelaku.
{a} nggak layak dieksekusi dari alasan begitu saja.
aku yakin {a} bukan orang jahat, hasilku membersihkan dia.
{a} jangan diseret, penjelasan waktunya masih masuk akal sih.
gw menolak vote ke {a}, tuduhannya cuma dugaan.
{a} bukan pelakunya menurutku, jeda chat itu bukan bukti.
aku percaya {a} Civilian dari hasil Peek yang kudapat.
{a} aman dari tuduhan itu, aku nggak melihat alasan vote dia.
gw nggak mau buang {a}, keterangan malamnya masih konsisten.
''')
AGREE_O=lines('''
gw curiga {a}, klaim role-nya seperti dibuat-buat.
vote {a} jadi pilihanku, alasan pindah suaranya janggal.
{a} ngarang hasil malam menurutku, jangan langsung dipercaya.
aku nggak percaya {a}, alibinya berubah tiap ditanya.
{a} paling sus, motif mengulur diskusinya bikin ragu.
gw pilih {a} buat divote, klaim Spy itu terasa palsu.
{a} kelihatan nutupin pelaku, aku curiga dari cara jawabnya.
aku akan menuduh {a}, penjelasan skillnya saling bertabrakan.
{a} bohong soal kapan hasil muncul menurutku.
gw nggak beli cerita {a}, itu seperti alibi palsu sih.
ayo vote {a}, arah pembicaraannya makin mencurigakan.
{a} seperti sengaja membuat salah vote, aku nggak percaya dia.
''')

MAIN_EDITS={
'r000417_v02':'soal dia yang tadi jadi bahasan awal, aku bela. Salah sebut ronde tidak otomatis berarti pelaku.',
'r000576_v02':'kalau mengikuti urutan yang diceritakan {c}, {a} justru bebas dari tuduhan malam itu.',
'r002378_v02':'boleh bahas klaim {a} sebagai Spy dulu, belum ada kesimpulan lain.',
'r002768_v02':'boleh jelaskan urutan aksi malamnya, {a}? Aku ingin tahu runtutnya.',
'r003743_v02':'{a}, boleh tuliskan role yang ingin kamu sebut tanpa menyebut target skill dulu?',
'r003913_v02':'{a} tidak patut dieksekusi dari bukti itu, {c} sendiri cuma menyebut jeda chat.',
'r003992_v02':'kamu menggunakan Guard pada malam keberapa? Aku cuma ingin tahu urutannya.',
'r003279_v02':'aku percaya dia warga. Tadi jawabannya masih nyambung sama urutan malam.',
'r000981_v02':'dari cerita {c}, gw curiga ke {a}; urutan aksinya berubah dua kali.',
'r001585_v02':'menurut cerita {c}, {a} tahu detail yang belum dibahas; aku curiga berat.',
'r001753_v02':'coba baca pesan {c}, yang bikin aku curiga {a} itu pergantian klaimnya.',
'r001757_v02':'{a} mungkin bersih dari cerita ini, sedangkan {b} makin mencurigakan setelah pindah vote.',
'r000194_v02':'{b} terlalu rapi mengalihkan isu, aku nggak percaya dia; {a} jangan ikut divote.',
'r001825_v02':'jangan vote {a} dulu; kalau harus menetapkan pilihan, aku pilih eksekusi {b}.',
'r001945_v02':'dia nggak pantas dituduh setelah urutannya jelas; {b} yang menurutku sengaja merusak urutan itu.',
'r001904_v02':'{b} sedang mengarang menurutku. Alasan {a} bisa dipercaya karena waktunya sesuai urutan chat.',
'r003746_v02':'dari seluruh cerita tadi, dia layak dicurigai karena tahu detail yang belum diumumkan.',
'r002355_v02':'dia bukan Hitman. Klaim yang kita bahas pertama masih cocok dengan urutan kejadian.',
'r000811_v02':'aku rasa dia bersih, bukan seperti yang dikhawatirkan di awal. Penjelasannya masih masuk akal.',
'r002908_v02':'aku sudah membandingkan ceritanya; dia yang sedang kita bahas itu paling layak dieksekusi.',
'r005162_v02':'aku tidak ngarang hasil Peek, jadi jangan eksekusi aku sebelum penjelasanku terbaca.',
'r003719_v02':'buat kamu yang tadi minta penjelasannya dibaca, tuduhan ke kamu belum terbukti; aku bela.',
'r003353_v02':'balik menjawab yang minta dicek, kamu tidak bersalah dari cerita yang kubaca.',
'r003557_v02':'mereka bukan Hitman, hasil Peek-ku justru menyebut keduanya Civilian.',
'r001762_v02':'vote {b} dan {a} jadi pilihanku, dua klaim itu bertentangan dengan urutan malam.',
'r003232_v02':'jangan buru-buru vote {a} juga {b}; keduanya cuma terlambat membaca pesan.',
'r000659_v02':'balik ke orang tadi, dia tidak bersalah dari hasil Peek-ku. Tolong tahan vote itu.',
'r003846_v02':'aku mau memastikan satu hal: {a} yang mengaku Spy tadi, kan?',
}
INTENT_EDITS={
5:'hasil Peek-ku ke Niken aman kok, nggak ada yang bilang dia pelaku',
11:'hasil skill Stalker-ku menunjukkan Cakra Civilian, jadi jangan vote dia',
19:'hasil peek semalam buat si L: Civilian, jangan salah vote nih',
30:'Kinanti tidak masuk Hitman dari cek Peek semalam, jangan buru-buru tuduh dia',
38:'peek ke Banyu selesai, hasilnya bukan Hitman kok, jadi tahan vote itu',
45:'Khalisa bersih dari hasil skill-ku. Gw Stalker, dia bukan Hitman',
85:'Afifah punya hasil Peek Hitman di layar gw, aku pilih vote dia',
87:'aku klaim Spy dulu, habis ini mau cerita waktu pakai Guard',
90:'klaimku warga biasa, sekarang giliran buka role kan?',
97:'gw mengaku Spy, itu role yang mau kusebut di sini',
99:'aku mengaku Civilian pada ronde ini, belum ada info lain dari gw',
}

def main():
    baseline=json.loads((R/'sebelum_sessions.json').read_text(encoding='utf-8'))
    edits=[];result=[]
    for item in baseline:
        new=copy.deepcopy(item);job=new['job'];ss=new['session'];ms=ss['messages']
        case,i=job['case_name'],job['case_index']
        s,a,b,c,e=random.Random(job['job_id']).sample(NAMES,5)
        names=dict(s=s,a=a,b=b,c=c,e=e)
        def settext(k,text):ms[k]['teks_chat']=text.format(**names)
        if case=='reference_start':
            for pos,text in enumerate(THREADS[i]):settext(pos,text)
        elif case=='ambiguous':
            settext(0,PAIR[i//2]);settext(1,PAIR_REPLY[i])
        elif case=='plural_reference':
            settext(0,PAIR[i]);settext(1,PAIR_REPLY[50+i])
        elif case=='self':
            settext(0,PAIR[i//2]);settext(1,GROUP[100+i])
        elif case=='multiple_targets':settext(0,PAIR[i])
        elif case=='mixed_relations':
            settext(0,NAMED[i%25]);settext(1,GROUP[50+i])
        elif case=='witness':
            own=ms[-1]['target'][0]['pemain']==s
            if own:settext(0,PEEK_ACC[i//4])
            else:settext(0,NAMED[i%25])
            settext(1,GROUP[i])
        elif case=='short_history_1':
            if ms[-1]['label_intent']=='defend':settext(0,ACC[i//2])
            elif ms[-1]['label_intent']=='offend':settext(0,ROLE[i//4])
            elif lt.mentions(ms[-1]['teks_chat'],a):settext(0,NAMED[(i//4+7)%25])
            else:settext(0,['{s}, role kamu apa dan ada aksi yang mau diceritakan nggak?',
                           'gw mau tanya role atau aksi yang kamu pakai semalam, {s}.',
                           '{s}, boleh jawab jenis skill atau role-mu dong?',
                           'apa yang ingin kamu laporkan soal role malam ini, {s}?',
                           '{s}, sekarang aku ingin dengar role atau aksi darimu.',
                           'kamu mau jelasin role atau penggunaan skill apa, {s}?'][i//8])
        elif case=='rhetorical_question':
            text=ms[-1]['teks_chat'].casefold()
            if 'spy' in text:
                settext(0,{1:'gw mengaku Spy, urutan Guard yang kupakai sudah kujelaskan.',
                           9:'aku klaim Spy dan sudah menjelaskan kapan pakai Guard.',
                           21:'gw Spy, cerita penggunaan skill-ku sudah ada di atas.'}.get(i,ROLE[13+i]))
            elif 'civilian' in text and ms[-1]['label_intent']=='offend':settext(0,'aku Civilian, itu pengakuan role yang kusampaikan sekarang.')
            elif 'peek' in text:
                settext(0,{8:'gw baru selesai menjelaskan urutan waktu dan klaim role tadi.',
                           15:'aku Stalker dan sudah melaporkan hasil Peek yang ingin dibahas.',
                           18:'aku sudah memberi penjelasan sampai akhir, sekarang mau dengar grup.'}.get(i,ROLE[13+i]))
            else:settext(0,ROLE[13+i])
        elif case=='second_person':
            settext(0,REQUEST[i])
            if i%2:
                settext(1,TIMERS[i]);settext(2,WAIT[i//2])
            else:
                settext(1,REPLY[i//2]);settext(2,TIMERS[i])
        elif case=='agreement':
            if ms[0]['label_intent']=='defend':settext(0,AGREE_D[(i//2)%13])
            else:settext(0,AGREE_O[(i//2)%12])
            settext(1,TIMERS[25+i])
        elif case=='interruption':
            if ms[0]['label_intent']=='offend':settext(0,ACC[i])
            else:settext(0,NAMED[i])
            settext(1,TIMERS[50+i]);settext(2,TIME_REPLY[i])
        elif case=='neutral_status':
            if i%3==0:settext(0,NAMED[i])
            elif i%3==1:settext(0,lines('''
{s}, role apa yang mau kamu ungkap sekarang?
gw ingin tanya ke kamu, {s}, klaim role-mu apa?
{s}, kamu sudah pakai skill atau baru mau menyebut role?
boleh cerita aksi atau role-mu malam ini, {s}?
{s}, apakah kamu udah memakai Peek sejak permainan dimulai?
gw nanya soal aksi malam yang kamu lakukan, {s}.
{s}, ada role atau aksi malam yang mau kamu laporkan?
kapan kamu memakai skill itu, {s}, malam pertama atau kedua?
''')[i//3])
            else:settext(0,ROLE[38+i//3])
        elif case!='first_message_unknown':raise AssertionError(case)
        if job['job_id'] in MAIN_EDITS:settext(-1,MAIN_EDITS[job['job_id']])
        # Karantina seluruh tema pencatatan pada pesan utama yang belum tercakup.
        if 'catat' in ms[-1]['teks_chat'].casefold() and job['job_id'] not in MAIN_EDITS:
            # Penggantian semantik terbatas: semua bentuk catat dibaca dan diperiksa ulang.
            old=ms[-1]['teks_chat']
            replacements={
                'untuk catatan ronde ini':'pada ronde ini',
                'untuk catatan bersama':'buat dibahas bersama',
                'Aku sedang mencatat.':'Aku ingin tahu urutannya.',
                'aku sedang mencatat.':'aku ingin tahu urutannya.',
                'Aku cuma mencatat urutannya.':'Aku cuma ingin tahu urutannya.',
                'Aku ingin menyalin tanpa salah tulis.':'Aku ingin memastikan yang tadi kudengar.',
                'boleh catat klaim':'boleh bahas klaim',
                'role yang ingin dicatat':'role yang ingin kamu sebut',
                'itu informasi role-ku buat pertanyaanmu tadi':'itu informasi role-ku buat pertanyaanmu tadi',
            }
            for x,y in replacements.items():old=old.replace(x,y)
            if 'catat' in old.casefold():raise ValueError(('Main perlu revisi tertulis',job['job_id'],old))
            ms[-1]['teks_chat']=old
        for n,(before,after) in enumerate(zip(item['session']['messages'],ms),1):
            assert {k:v for k,v in before.items() if k!='teks_chat'}=={k:v for k,v in after.items() if k!='teks_chat'}
            if before['teks_chat']!=after['teks_chat']:
                edits.append(dict(session_id=job['job_id'],posisi=n,sebelum=before,sesudah=after,
                    aturan='Revisi 1: gaya percakapan game; pengirim, label, target, bukti, jumlah/urutan pesan dipertahankan.'))
        lt.validate_session(ss,job)
        result.append(dict(job_id=job['job_id'],session=ss))
    # Urutan job/prompt tetap seperti sumber, bukan urutan nama file baseline.
    byid={r['job_id']:r for r in result}
    jobs=json.loads((F/'jobs.json').read_text(encoding='utf-8'))
    out=F/'hasil_revisi1';out.mkdir(exist_ok=True)
    for offset in range(0,500,10):
        batch=[byid[j['job_id']] for j in jobs[offset:offset+10]]
        (out/f'{offset//10+1:03d}_codex_revisi1.txt').write_text(json.dumps({'results':batch},ensure_ascii=False,indent=2),encoding='utf-8')
    (R/'revisi_log.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in edits),encoding='utf-8')
    (R/'sesi_draft.json').write_text(json.dumps(result,ensure_ascii=False),encoding='utf-8')
    # Intent yang tidak melanggar dibiarkan identik.
    manifest=json.loads((R/'sebelum_intent_manifest.json').read_text(encoding='utf-8'))
    intent_edits=[]
    for r in manifest:
        if r['row'] in INTENT_EDITS:
            old=r['teks_chat'];r['teks_chat']=INTENT_EDITS[r['row']]
            intent_edits.append(dict(row=r['row'],sebelum=old,sesudah=r['teks_chat'],label_intent=r['label_intent'],pattern=r['pattern']))
    (R/'intent_draft.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    (R/'revisi_intent.json').write_text(json.dumps(intent_edits,ensure_ascii=False,indent=2),encoding='utf-8')
    rows=[lt.make_record(r['session']) for r in result]
    print(json.dumps(metrics(rows,manifest),ensure_ascii=False,indent=2))
    print('Revisi pesan',len(edits),'revisi intent',len(intent_edits))

if __name__=='__main__':main()
