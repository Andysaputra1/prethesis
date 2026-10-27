"""Susun jawaban JSON dari kalimat yang ditulis Codex, tanpa layanan/model eksternal."""
import csv, json, random
from pathlib import Path
from collections import Counter
from kalimat import entries
from konteks import AMBIG, PAIR_FOLLOW, SELF_CONTEXT, ACCUSATIONS, ROLE_CLAIMS, REQUESTS, TIMERS, THREADS
from konteks_lanjutan import EXTRA
from rencana import QUOTAS

FOLDER=Path(__file__).resolve().parents[1]
DATA=FOLDER.parent
NAMES='Sekar Kirana Niken Pram Wening Larasati Baskara Cakra Prabu Mahesa Pandu Satya Yudhis Aruna Aksara Renata Keisha Nadira Naura Salma Safira Almira Anindya Kinanti Ajeng Ayuning Rengga Raksa Tirta Banyu Damar Jalu Bagaskara Wardana Mahira Khalisa Nadhif Haris Syauqi Haikal Zafran Rasyid Ghani Ghina Syifa Tsania Syakira Aisyah Khansa Fathia Afifah Atika Amel Anisa Arum Asih Astri Ayunda Cahya Cantika Deandra Delima Diandra Dyah Embun Erlina Febi Febrian Feby Ferdi Gendis Ghea Habib Hafiz Halim Hanif Hilmi Inaya Isna Izza Jauhar Kautsar Kemal Kresna Lintang Luthfan Mahdi Marsha Mutiara Nabil Nadya Najwa Naufala Nayla Nirmala Noval Okta Priska Prita Rahma Raisa Ratih Ratu Rayhan Rizal Rizki Rosita Sabrina Sakti Salsabila Savira Shafa Shinta Suci Tania Tasya Thalia Tiara Tisna Tria Utari Vanya Vanya Wulan Yasmin Yumna Zahira Zakia Zulfikar'.split()
old=list(csv.DictReader((DATA/'dataset_final3_context_target_pilot25_lengkap.csv').open(encoding='utf-8-sig',newline='')))
excluded={n.casefold() for r in old for n in json.loads(r['daftar_pemain'])}
excluded.update(n.casefold() for n in 'Agus Bella Candra Desi Erik Fitri Galang Hesti Irwan Jessi'.split())
NAMES=sorted(set(n for n in NAMES if n.casefold() not in excluded))

def make_session(job):
    case,i=job['case_name'],job['case_index']
    rows=entries(case)
    assert len(rows)==QUOTAS[case],(case,len(rows))
    kind,raw=rows[i]
    label={'d':'defend','w':'defend','o':'offend','n':'neutral'}[kind]
    assert label==job['source']['label_intent']
    rng=random.Random(job['job_id'])
    s,a,b,c,e=rng.sample(NAMES,5)
    names=dict(s=s,a=a,b=b,c=c,e=e)
    roster=[s,a,b,c,e]; rng.shuffle(roster)
    ms=[]
    def add(sender,text,label='neutral',targets=()):
        # targets: (player, relation, evidence); all evidence preserved in checkpoints.
        ms.append(dict(pengirim=sender,teks_chat=text.format(**names),label_intent=label,
            target=[dict(pemain=p,relasi=r,bukti_pesan=ev) for p,r,ev in targets]))
    def rel(p,r='neutral',ev=None): return (p,r,ev if ev is not None else [len(ms)+1])
    focus=a
    if case=='ambiguous':
        add(c,AMBIG[i//2],targets=[rel(a),rel(b)])
        follow=PAIR_FOLLOW[(i//2)%5]
        # "dua klaim" juga mengacu kedua pemain yang sudah disebut.
        add(e,follow,targets=[rel(a,ev=[1]),rel(b,ev=[1])])
        targets=[rel('tidak_diketahui',label,[])]; focus=''
    elif case=='witness':
        if kind=='w':
            add(c,'hasil Peek yang aku laporkan menyebut {s} Hitman, aku curiga {s}.','offend',[rel(s,'offend')])
        else:
            introductions=[
                'aku punya salinan urutan chat {a}; nanti bisa dipakai buat pembahasan.',
                'catatanku tentang {a} sudah kubagikan ke grup sebelum sesi ini.',
                'aku menyimpan laporan soal {a}, termasuk bagian nomor malam dan klaim role.',
                'ada ringkasan pesan {a} di catatanku; isinya bisa kita baca bersama.',
                'aku baru selesai menyalin keterangan {a} ke ringkasan ronde.',
            ]
            add(c,introductions[(i//2)%5],targets=[rel(a)])
        add(b,['semua boleh menanggapi catatan yang sudah dibagikan.','urutan pesannya masih tersimpan di chat grup.','silakan lanjut, kolom diskusinya masih terbuka.','kita masih membahas ringkasan ronde ini.','aku sedang menyalin pesan ke catatan sendiri.'][i%5])
        focus=s if kind=='w' else a
        targets=[rel(focus,label)]
    elif case=='mixed_relations':
        # a remains sole third-person topic; b has not appeared in context.
        add(c,['sekarang kita baca keterangan {a} soal malam tadi.','{a} sudah mengirim penjelasan, kita bahas bagian itu dulu.','catatan yang sedang terbuka adalah milik {a}.','aku menaruh keterangan {a} pada bagian awal ringkasan.','kita sedang meninjau klaim {a} sebelum pindah topik.'][i%5],targets=[rel(a)])
        add(e,['aku membaca urutan waktunya dulu.','silakan bahas, semua bisa menyampaikan penilaian.','bagian klaim dan bagian hasilnya sudah terpisah di catatan.','teks yang masuk belum berubah sejak disalin.','kita pakai nomor malam yang sama saat membacanya.'][i%5])
        targets=[rel(a,'defend',[1] if '{a}' not in raw else [3]),rel(b,'offend')]
    elif case=='reference_start':
        intro,thread=(THREADS+EXTRA)[i]
        add(c,intro,targets=[rel(a)])
        for j,line in enumerate(thread.strip().splitlines()):
            add([b,e,s,c][j%4],line)
        assert len(ms)==12
        targets=[rel(a,label,[1])]
    elif case=='self':
        add(c,SELF_CONTEXT[(i//2)%5],targets=[rel(a),rel(b)])
        add(e,['semua yang belum menjelaskan boleh lanjut sekarang.','silakan lanjut ke penjelasan berikutnya, waktu diskusi masih ada.','yang ingin memberi tanggapan boleh mengetik di grup.','catatan ronde ini masih terbuka untuk ditambahkan.','aku menyimak pesan berikutnya sambil membaca urutan chat.'][(i//2)%5])
        targets=[rel(s,label)]; focus=s
    elif case=='short_history_1':
        if label=='defend':
            add(a,ACCUSATIONS[(i//2)%len(ACCUSATIONS)],'offend',[rel(s,'offend')])
            targets=[rel(s,label)]; focus=s
        elif label=='offend':
            add(a,ROLE_CLAIMS[(i//4)%len(ROLE_CLAIMS)])
            targets=[rel(a,label,[2] if '{a}' in raw else [1])]
        elif '{a}' in raw:
            add(c,'{a} sudah mengirim catatan role dan waktu skill yang disebutnya.',targets=[rel(a)])
            targets=[rel(a)]
        else:
            add(a,'{s}, apa role atau aksi yang ingin kamu laporkan untuk catatan ronde ini?',targets=[rel(s)])
            targets=[rel(a,ev=[1])]
    elif case=='second_person':
        add(a,REQUESTS[i%5],targets=[rel(s)])
        add(s,'aku akan baca catatanmu dulu sebelum memberikan penilaian.',targets=[rel(a,ev=[1])])
        if i%2==0:
            add(c,TIMERS[i%5])
        else:
            add(a,'{s}, aku masih menunggu tanggapan soal klaim yang kuminta tadi.',targets=[rel(s)])
        targets=[rel(a,label,[1])]
    elif case=='plural_reference':
        add(e,AMBIG[i],targets=[rel(a),rel(b)])
        add(c,'aku sedang membaca catatan kedua orang itu sebelum memberi pendapat.',targets=[rel(a,ev=[1]),rel(b,ev=[1])])
        targets=[rel(a,label,[1]),rel(b,label,[1])]
    elif case=='rhetorical_question':
        add(a,'aku sudah menuliskan klaim role dan penjelasan waktunya di chat.')
        targets=[rel(a,label,[1])]
    elif case=='agreement':
        # Four deliberate rebuttals of an accusation; otherwise agree with source.
        disagree=i in {8,10,20,24}
        context_label='offend' if disagree else label
        if context_label=='offend':
            txt=['aku curiga {a}, klaimnya terdengar palsu.','vote {a} jadi saranku karena alasan pindah pilihannya janggal.','{a} itu ngarang soal hasil malam menurutku.','aku nggak percaya {a}, alibinya berubah terus.','yang paling sus bagiku {a}, motifnya mengulur pembahasan aneh.'][i%5]
        else:
            txt=['{a} bukan Hitman menurutku, jangan dieksekusi.','aku bela {a}, hasil Peek-ku membersihkan dia.','tuduhan ke {a} belum terbukti, aku menolak vote itu.','{a} aman, keterlambatan chatnya masih masuk akal.','aku percaya {a} warga; jeda mengetik tidak membuatnya jadi pelaku.'][i%5]
        add(c,txt,context_label,[rel(a,context_label)])
        add(e,TIMERS[i%5])
        targets=[rel(a,label,[1])]
    elif case=='multiple_targets':
        add(c,'catatan yang sedang kita bahas milik {a} dan {b}, masing-masing sudah menulis klaim.',targets=[rel(a),rel(b)])
        targets=[rel(a,label),rel(b,label)]
    elif case=='interruption':
        own=label=='defend' and i%4==0
        if own:
            add(c,ACCUSATIONS[(i//4)%len(ACCUSATIONS)],'offend',[rel(s,'offend')])
        else:
            add(c,'pembahasan kita masih tentang klaim {a} dan alasan jeda chatnya.',targets=[rel(a)])
        add(b,TIMERS[i%5])
        add(e,['di layarku hitungannya sama, masih sesi diskusi.','aku sudah melihat timernya, silakan teruskan pembahasan.','oke, penanda waktunya sudah terlihat untuk semua.','belum berganti ronde, kolom diskusi tetap terbuka.','pengingatnya sudah terbaca, kita bisa lanjut.'][i%5])
        focus=s if own else a
        targets=[rel(focus,label,[4] if own or '{a}' in raw else [1])]
    elif case=='first_message_unknown':
        targets=[rel('tidak_diketahui',label,[])]; focus=''
    elif case=='neutral_status':
        if i%3==0:
            add(c,'{a} sedang menulis keterangan role untuk catatan bersama.',targets=[rel(a)])
            targets=[rel(a)]+([rel(b)] if '{b}' in raw else [])
        elif i%3==1:
            add(a,'{s}, bisa jawab apa role atau aksi yang kamu laporkan malam ini?',targets=[rel(s)])
            targets=[rel(a,ev=[1])]
        else:
            add(a,'aku sudah menyiapkan catatan tentang role dan waktu penggunaan skill.')
            targets=[rel(a,ev=[1])]
    else: raise AssertionError(case)
    add(s,raw,label,targets)
    assert len(ms)==job['jumlah_pesan'],(case,i,len(ms))
    return dict(case_name=case,participants=roster,focus_player=focus,panggilan=[],messages=ms)

def main():
    jobs=json.loads((FOLDER/'jobs.json').read_text(encoding='utf-8'))
    for offset in range(0,len(jobs),10):
        batch=jobs[offset:offset+10]
        # Read corresponding prompt as the contract for this batch.
        prompt=(FOLDER/'prompt'/f'prompt_{offset//10+1:03d}.txt').read_text(encoding='utf-8')
        assert all(j['job_id'] in prompt for j in batch)
        result={'results':[dict(job_id=j['job_id'],session=make_session(j)) for j in batch]}
        path=FOLDER/'hasil'/f'{offset//10+1:03d}_codex.txt'
        path.write_text('```json\n'+json.dumps(result,ensure_ascii=False,indent=2)+'\n```\n',encoding='utf-8')
    print('500 sesi ditulis ke 50 jawaban JSON; roster baru:',len(NAMES),'nama')

if __name__=='__main__': main()
