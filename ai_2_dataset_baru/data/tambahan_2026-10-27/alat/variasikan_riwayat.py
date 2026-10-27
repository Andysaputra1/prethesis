"""Ganti 40 riwayat reference_start yang berulang, sambil menjaga jejak revisi."""
from pathlib import Path
import copy,json
import label_target as lt
from konteks_lanjutan import EXTRA
FOLDER=Path(__file__).resolve().parents[1]

def main():
    changed=[]
    for file in sorted((FOLDER/'sessions').glob('*.json')):
        item=json.loads(file.read_text(encoding='utf-8'));j=item['job'];ss=item['session']
        if j['case_name']!='reference_start' or j['case_index']<10:continue
        intro,thread=EXTRA[j['case_index']-10]
        lines=[intro.format(a=ss['focus_player']),*thread.strip().splitlines()]
        for index,text in enumerate(lines):
            before=copy.deepcopy(ss['messages'][index])
            ss['messages'][index]['teks_chat']=text
            after=ss['messages'][index]
            if before!=after:
                changed.append(dict(session_id=j['job_id'],posisi=index+1,sebelum=before,sesudah=copy.deepcopy(after),
                    aturan='N-a/N-b/N-c/N-e: informasi/pertanyaan grup tanpa serangan atau pembelaan. Nama focus hanya di awal; 40 utas baru menghapus pengulangan riwayat panjang.'))
        lt.validate_session(ss,j)
        file.write_text(json.dumps(item,ensure_ascii=False,indent=2),encoding='utf-8')
    with (FOLDER/'revisi_log.jsonl').open('a',encoding='utf-8') as h:
        for row in changed:h.write(json.dumps(row,ensure_ascii=False)+'\n')
    print('Revisi riwayat panjang:',len(changed),'pesan pada',len({r['session_id'] for r in changed}),'sesi')
    jobs=json.loads((FOLDER/'jobs.json').read_text(encoding='utf-8'))
    items=[json.loads((FOLDER/'sessions'/f"{j['job_id']}.json").read_text(encoding='utf-8')) for j in jobs]
    tmp=FOLDER/'alat'/'_export_setelah_review.csv'
    lt.export_records(items,tmp,None)
    tmp.replace(FOLDER.parent/'dataset_target_tambahan.csv')

if __name__=='__main__':main()
