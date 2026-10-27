"""Perbaikan hasil pembacaan makna; sebelum/sesudah setiap pesan dicatat utuh."""
from pathlib import Path
import json,copy
from konteks import TIMERS
import label_target as lt

FOLDER=Path(__file__).resolve().parents[1]

def main():
    log=FOLDER/'revisi_log.jsonl'
    revisions=[]; reviewed=[]
    # Hilangkan rujukan yang dapat terbaca sebagai pembicara pertama,
    # dan cocokkan selingan timer dengan teks utama pada orang kedua.
    replacements={
        9:'dari seluruh catatan tadi, dia layak dicurigai karena tahu detail yang belum diumumkan.',
        35:'balik ke klaim yang sedang kita urutkan, dia tidak pantas dibuang karena salah baca nomor malam.',
        49:'aku sudah membandingkan catatannya; dia yang sedang kita bahas itu paling layak dieksekusi.',
    }
    for file in sorted((FOLDER/'sessions').glob('*.json')):
        item=json.loads(file.read_text(encoding='utf-8'));job=item['job'];ss=item['session'];ms=ss['messages']
        case,i=job['case_name'],job['case_index']
        before=copy.deepcopy(ms)
        if case=='second_person' and i%2:
            # Pesan 3 tetap dari peminta penilaian. Pesan 2 menjadi selingan timer.
            sender=next(n for n in ss['participants'] if n not in {ms[0]['pengirim'],ms[-1]['pengirim']})
            ms[1]=dict(pengirim=sender,teks_chat=TIMERS[i%5],label_intent='neutral',target=[])
        if case=='rhetorical_question':
            text=ms[-1]['teks_chat'].casefold()
            if 'spy' in text: claim='aku mengaku Spy, catatan penggunaan Guard-ku akan kutulis di sini.'
            elif 'civilian' in text: claim='aku Civilian, itu role yang ingin kucatat pada ronde ini.'
            elif 'peek' in text: claim='aku Stalker dan sudah menulis hasil Peek ke catatan ronde.'
            else: claim=ms[0]['teks_chat']
            ms[0]['teks_chat']=claim
        if case=='reference_start' and i in replacements:
            # Indeks 35 adalah offend: jangan mengganti intent; pakai tuduhan yang sesuai.
            if i==35:
                ms[-1]['teks_chat']='dia seperti sengaja mengaburkan nomor malam dalam klaimnya; aku curiga itu alibi palsu.'
            else: ms[-1]['teks_chat']=replacements[i]
        for pos,(old,new) in enumerate(zip(before,ms),1):
            if old!=new:
                revisions.append(dict(session_id=job['job_id'],posisi=pos,sebelum=old,sesudah=new,
                    aturan='Keterlacakan acuan dan koherensi dialog; N-c untuk selingan grup, N-a untuk klaim murni. Intent utama tetap mengikuti ATURAN_LABEL.'))
        lt.validate_session(ss,job)
        if ms!=before:file.write_text(json.dumps(item,ensure_ascii=False,indent=2),encoding='utf-8')
        reviewed.append(dict(session_id=job['job_id'],case_name=case,messages=len(ms),
            review='Ditinjau Codex: teks utama dan seluruh pola konteks, efek intent, sumber/sapaan vs target, bukti acuan. Bukan verifikasi manusia/model independen.'))
    with log.open('a',encoding='utf-8') as h:
        for r in revisions:h.write(json.dumps(r,ensure_ascii=False)+'\n')
    (FOLDER/'alat/review_semantik.json').write_text(json.dumps(reviewed,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Ditinjau:',len(reviewed),'sesi; revisi pesan:',len(revisions))

if __name__=='__main__':main()
