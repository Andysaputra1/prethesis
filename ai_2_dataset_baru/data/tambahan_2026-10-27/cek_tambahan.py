"""Pemeriksaan ulang plan03. Tidak menjalankan notebook/training atau memodifikasi sumber.

Jalankan dari repo: venv\Scripts\python.exe ai_2_dataset_baru/data/tambahan_2026-10-27/cek_tambahan.py
"""
import argparse, ast, csv, hashlib, json, re, sys
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path
import pandas as pd

HERE=Path(__file__).resolve().parent
DATA=HERE.parent
ROOT=HERE.parents[2]
sys.path.insert(0,str(HERE/'alat'))
import label_target as lt
from rencana import QUOTAS,labels_for
from gaya_revisi1 import validate_style

def require(condition,message):
    if not condition: raise ValueError(message)

def norm(text): return ' '.join(text.casefold().split())

def read_csv(path):
    with Path(path).open(encoding='utf-8-sig',newline='') as h:
        reader=csv.DictReader(h); rows=list(reader)
        require(all(None not in row and None not in row.values() for row in rows),f'CSV rusak: {path}')
        return reader.fieldnames,rows

def check_message(m,players,where):
    require(m['label_intent'] in {'offend','defend','neutral'},f'{where}: label tidak sah')
    require(m['pengirim'] in players,f'{where}: pengirim di luar roster')
    require(isinstance(m['teks_chat'],str) and m['teks_chat'].strip(),f'{where}: teks kosong')
    require(isinstance(m['target'],list),f'{where}: target bukan list')
    relations=set(); seen=set()
    for t in m['target']:
        require(set(t)=={'pemain','relasi'},f'{where}: format target keliru')
        require(t['pemain'] in players or t['pemain']=='tidak_diketahui',f'{where}: target di luar roster')
        require(t['pemain'] not in seen,f'{where}: target ganda/kontradiktif'); seen.add(t['pemain'])
        require(t['relasi'] in {'offend','defend','neutral'},f'{where}: relasi asing'); relations.add(t['relasi'])
    if m['label_intent']=='neutral':
        require(relations<={'neutral'},f'{where}: neutral harus berelasi neutral/kosong')
    else:
        require(m['target'] and 'neutral' not in relations,f'{where}: non-neutral tanpa target/berelasi neutral')
        require(m['label_intent'] in relations,f'{where}: intent tidak muncul dalam relasi')
        require(not (m['label_intent']=='defend' and 'offend' in relations),f'{where}: offend harus diutamakan')

def similar_pairs(texts,threshold=.9):
    """Ambang ketat > .9, cek kedua arah karena SequenceMatcher bisa asimetris."""
    normalized=[norm(t) for t in texts]; matches=[]
    for i,a in enumerate(normalized):
        for j in range(i):
            b=normalized[j]
            sm=SequenceMatcher(None,a,b)
            # Batas atas aman; bukan mengganti ukuran kemiripan yang diminta.
            if sm.real_quick_ratio()<=threshold or sm.quick_ratio()<=threshold:
                continue
            ratio=max(sm.ratio(),SequenceMatcher(None,b,a).ratio())
            if ratio>threshold:matches.append((j,i,round(ratio,6)))
    return matches

def run_loader(path):
    nb=json.loads((ROOT/'ai_2_dataset_baru/nlu_target.ipynb').read_text(encoding='utf-8'))
    found=[]
    for cell in nb['cells']:
        s=''.join(cell.get('source',[]))
        if cell['cell_type']=='code' and 'def load_target_dataset(' in s:
            found.extend(n for n in ast.parse(s).body if isinstance(n,ast.FunctionDef) and n.name=='load_target_dataset')
    require(len(found)==1,'Loader notebook tidak ditemukan secara tunggal')
    # Kompilasi hanya fungsi loader; tidak ada cell training/import model dijalankan.
    module=ast.Module(body=found,type_ignores=[])
    ns=dict(Path=Path,pd=pd,json=json,JSON_COLUMNS=['chat_sebelumnya','daftar_pemain','target'])
    exec(compile(ast.fix_missing_locations(module),'notebook_loader_only','exec'),ns)
    _,report=ns['load_target_dataset'](path)
    return report

def validate_target(path):
    old_path=DATA/'dataset_final3_context_target_pilot25_lengkap.csv'
    expected,old=read_csv(old_path)
    header,rows=read_csv(path)
    require(header==expected,'Header/urutan 13 kolom berbeda dari file lama')
    pd.read_csv(path,keep_default_na=False)
    require(len(rows)==500,f'Target harus 500, ditemukan {len(rows)}')
    ids=[r['session_id'] for r in rows]
    require(len(ids)==len(set(ids)),'session_id duplikat')
    require(not set(ids)&{r['session_id'] for r in old},'session_id bocor ke data lama')
    require(all(re.fullmatch(r'r\d{6}_v02',x) for x in ids),'session_id harus berakhiran _v02')
    old_groups={r['source_group'] for r in old}
    require(not {r['source_group'] for r in rows}&old_groups,'source_group bocor ke data lama')
    require(len({r['source_group'] for r in rows})==len(rows),'Sumber baru tidak unik')
    counts=Counter(r['case_name'] for r in rows)
    require(set(counts)==set(QUOTAS),'Daftar kasus keliru/original tidak boleh dibuat')
    for case,q in QUOTAS.items():
        require(abs(counts[case]-q)<=2,f'Kuota {case}: {counts[case]}, seharusnya {q} +/-2')
        actual=Counter(r['label_intent'] for r in rows if r['case_name']==case)
        require(actual==Counter(labels_for(case,counts[case])),f'Komposisi label {case} keliru: {actual}')
    jobs=json.loads((HERE/'jobs.json').read_text(encoding='utf-8'))
    job_map={j['job_id']:j for j in jobs}
    require(set(ids)==set(job_map),'CSV tidak sama dengan daftar jobs')
    source={r['source_row']:r for r in lt.read_source(DATA/'dataset_final3.csv')}
    old_texts={norm(r['teks_chat']) for r in old}
    old_messages=old_texts|{norm(m['teks_chat']) for r in old for m in json.loads(r['chat_sebelumnya'])}
    old_names={n.casefold() for r in old for n in json.loads(r['daftar_pemain'])}
    reserved={n.casefold() for n in 'Agus Bella Candra Desi Erik Fitri Galang Hesti Irwan Jessi'.split()}
    context_total=0;self_replies=0;unknown_count=0;new_names=set();witness_self=0;second_earlier=0;self_interruption=0
    for r in rows:
        sid=r['session_id']; job=job_map[sid]
        for key in ['chat_sebelumnya','daftar_pemain','target','panggilan']:
            value=json.loads(r[key]);require(isinstance(value,list),f'{sid}: {key} bukan list')
            require(r[key]==json.dumps(value,ensure_ascii=False,separators=(',',':')),f'{sid}: JSON tidak kanonis {key}')
            r[key]=value
        players=set(r['daftar_pemain']);new_names.update(players)
        require(len(players)==len(r['daftar_pemain']),f'{sid}: roster duplikat')
        require(not {p.casefold() for p in players}&reserved,f'{sid}: nama semu notebook digunakan')
        require(r['synthetic_context']=='True' and r['direvisi']=='False',f'{sid}: metadata boolean keliru')
        require(len(r['chat_sebelumnya'])<=12,f'{sid}: konteks >12')
        main={k:r[k] for k in ['pengirim','teks_chat','label_intent','target']}
        check_message(main,players,sid)
        for i,m in enumerate(r['chat_sebelumnya']):check_message(m,players,f'{sid} konteks {i+1}')
        context_total+=len(r['chat_sebelumnya'])
        src=source.get(int(r['source_csv_row']))
        require(src is not None and src==job['source'],f'{sid}: provenance sumber tidak sesuai')
        require(src['source_group']==r['source_group'],f'{sid}: hash sumber keliru')
        require(norm(src['teks_chat']) not in old_texts,f'{sid}: kalimat sumber identik target lama')
        require(norm(r['teks_chat']) not in old_messages,f'{sid}: pesan utama identik pesan lama')
        require(r['case_name']==job['case_name'],f'{sid}: kasus salah')
        targets={t['pemain'] for t in r['target']};relations={t['relasi'] for t in r['target']}
        case=r['case_name'];hist=r['chat_sebelumnya']
        if case in {'ambiguous','first_message_unknown'}:
            require(targets=={'tidak_diketahui'},f'{sid}: unknown wajib');unknown_count+=1
        if case=='ambiguous':
            mentioned={p for p in players if lt.mentions(hist[0]['teks_chat'],p)}
            require(len(mentioned)>=2,f'{sid}: ambiguous harus punya >=2 calon')
        if case=='first_message_unknown':require(not hist and len(players)>=4,f'{sid}: pembuka/roster salah')
        if case=='mixed_relations':require(relations=={'offend','defend'},f'{sid}: campuran tidak lengkap')
        if case=='reference_start':require(len(hist)==12,f'{sid}: wajib 12 konteks')
        if case=='self':require(targets=={r['pengirim']},f'{sid}: self bukan pengirim saja')
        if case=='short_history_1':
            require(len(hist)==1,f'{sid}: wajib satu konteks')
            if r['label_intent']=='defend':
                require(targets=={r['pengirim']} and hist[0]['label_intent']=='offend' and
                    any(t=={'pemain':r['pengirim'],'relasi':'offend'} for t in hist[0]['target']),f'{sid}: pola bantahan diri salah')
                self_replies+=1
        if case=='neutral_status':require(relations=={'neutral'},f'{sid}: wajib contoh target neutral')
        if case=='witness' and r['label_intent']=='defend' and targets=={r['pengirim']}:witness_self+=1
        if case=='second_person' and hist[-1]['pengirim'] not in targets:second_earlier+=1
        if case=='interruption' and targets=={r['pengirim']}:self_interruption+=1
        checkpoint=json.loads((HERE/'sessions'/f'{sid}.json').read_text(encoding='utf-8'))
        require(checkpoint['job']==job,f'{sid}: checkpoint job berubah')
        lt.validate_session(checkpoint['session'],job)
        expected_record=lt.make_record(checkpoint['session'])
        require(all(r[k]==v for k,v in expected_record.items()),f'{sid}: export berbeda dari checkpoint')
        require(r['panggilan']==checkpoint['session']['panggilan'],f'{sid}: panggilan tidak sesuai')
    require(self_replies==25,'Harus ada 25 bantahan diri setelah satu tuduhan')
    require(witness_self>0 and second_earlier>0 and self_interruption>0,'Varian khusus tabel plan belum lengkap')
    matches=similar_pairs([r['teks_chat'] for r in rows])
    require(not matches,'Kemiripan >0.9: '+json.dumps([(ids[a],ids[b],v) for a,b,v in matches],ensure_ascii=False))
    return dict(rows=len(rows),per_case=dict(counts),per_label=dict(Counter(r['label_intent'] for r in rows)),
                context_messages=context_total,similar_pairs_over_09=matches,source_overlap=0,unknown=unknown_count,
                short_history_self_defense=self_replies,witness_self_defense=witness_self,
                second_person_not_last_speaker=second_earlier,interruption_self=self_interruption,
                new_names=len(new_names),names_shared_with_old=sorted(n for n in new_names if n.casefold() in old_names)),rows

def validate_intent(path):
    header,rows=read_csv(path);old_header,old=read_csv(DATA/'dataset_final3.csv')
    require(header==old_header==['teks_chat','label_intent'],'Header intent salah')
    require(len(rows)==100,'Intent harus 100 chat')
    expected=Counter(defend=70,offend=15,neutral=15)
    require(Counter(r['label_intent'] for r in rows)==expected,'Komposisi label intent bukan 70/15/15')
    texts=[norm(r['teks_chat']) for r in rows]
    require(len(set(texts))==100,'Duplikat intent baru')
    require(not set(texts)&{norm(r['teks_chat']) for r in old},'Duplikat intent dengan dataset lama')
    manifest=json.loads((HERE/'alat/intent_manifest.json').read_text(encoding='utf-8'))
    require(len(manifest)==len(rows),'Manifest intent salah')
    patterns=Counter()
    for i,(r,m) in enumerate(zip(rows,manifest),2):
        require(m['row']==i and all(r[k]==m[k] for k in r),f'Intent baris {i} berbeda manifest review')
        patterns[m['pattern']]+=1;t=norm(r['teks_chat'])
        if m['pattern']=='peek_membersihkan':
            require(r['label_intent']=='defend' and re.search(r'peek|intip|pengintai|skill|stalker',t) and
                    re.search(r'civilian|warga|aman|bersih|bebas|nggak jahat|tidak masuk hitman|bukan (?:hitman|pelaku)',t),f'Intent {i}: pola Peek membersihkan salah')
        elif m['pattern']=='peek_memberatkan':
            require(r['label_intent']=='offend' and re.search(r'hitman|pelaku',t) and re.search(r'peek|intip|pengintai|stalker|skill',t),f'Intent {i}: pola Peek memberatkan salah')
        elif m['pattern']=='klaim_pembelaan':
            require(r['label_intent']=='defend' and re.search(r'spy|civilian|stalker|warga',t) and
                    re.search(r'jangan|bukan|menolak|tidak benar|nggak bersalah|nggak melakukan|tidak melakukan|tuduhan',t),f'Intent {i}: klaim pembelaan salah')
        elif m['pattern']=='klaim_murni':
            require(r['label_intent']=='neutral' and re.search(r'spy|civilian|stalker|warga',t) and
                    not re.search(r'jangan|bukan hitman|tidak bersalah|nggak bersalah',t),f'Intent {i}: klaim murni salah')
        else: raise ValueError('Pola intent tidak dikenal')
    require(patterns==dict(peek_membersihkan=50,klaim_pembelaan=20,peek_memberatkan=15,klaim_murni=15),'Komposisi empat pola intent salah')
    return dict(rows=100,per_label=dict(expected),per_pattern=dict(patterns),duplicates=0)

def check_encoding(path,bom):
    raw=Path(path).read_bytes()
    require(raw.startswith(b'\xef\xbb\xbf')==bom,f'BOM salah: {path}')
    require(b'\n' not in raw.replace(b'\r\n',b'') and b'\r' not in raw.replace(b'\r\n',b''),f'Bukan CRLF: {path}')
    raw.decode('utf-8-sig')

def validate_revision(rows,intent_path):
    baseline=json.loads((HERE/'alat/revisi1/sebelum_sessions.json').read_text(encoding='utf-8'))
    byid={r['session_id']:r for r in rows}
    contexts_changed=0;main_changed=0
    for original in baseline:
        sid=original['job']['job_id']
        current=json.loads((HERE/'sessions'/f'{sid}.json').read_text(encoding='utf-8'))
        require(current['job']==original['job'],f'{sid}: identitas job berubah saat revisi')
        a,b=original['session'],current['session']
        require({k:v for k,v in a.items() if k!='messages'}=={k:v for k,v in b.items() if k!='messages'},f'{sid}: struktur sesi berubah saat revisi')
        require(len(a['messages'])==len(b['messages']),f'{sid}: panjang sesi berubah')
        for pos,(old,new) in enumerate(zip(a['messages'],b['messages'])):
            require({k:v for k,v in old.items() if k!='teks_chat'}=={k:v for k,v in new.items() if k!='teks_chat'},
                    f'{sid}: pengirim/label/target/bukti berubah di pesan {pos+1}')
            if old['teks_chat']!=new['teks_chat']:
                if pos==len(a['messages'])-1:
                    require(bool(re.search(r'catat|pembelaan',old['teks_chat'],re.I)),f'{sid}: perubahan utama di luar cakupan gaya')
                    main_changed+=1
                else:contexts_changed+=1
        expected=lt.make_record(b)
        require(all(byid[sid][k]==v for k,v in expected.items()),f'{sid}: hasil CSV tidak cocok dengan sesi revisi')
    _,old_rows=read_csv(DATA/'dataset_final3_context_target_pilot25_lengkap.csv')
    for r in old_rows:r['chat_sebelumnya']=json.loads(r['chat_sebelumnya'])
    _,old_intent=read_csv(DATA/'dataset_final3.csv')
    _,new_intent=read_csv(intent_path)
    before=json.loads((HERE/'alat/revisi1/sebelum_intent_manifest.json').read_text(encoding='utf-8'))
    require([r['label_intent'] for r in before]==[r['label_intent'] for r in new_intent],'Label/urutan intent berubah saat revisi')
    style=validate_style(rows,new_intent,old_rows,old_intent)
    return dict(annotations_and_structure_unchanged=True,contexts_changed=contexts_changed,
                main_changed=main_changed,intent_changed=sum(a['teks_chat']!=b['teks_chat'] for a,b in zip(before,new_intent)),**style)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target',type=Path,default=DATA/'dataset_target_tambahan.csv')
    parser.add_argument('--intent',type=Path,default=DATA/'dataset_intent_tambahan.csv')
    args=parser.parse_args()
    try:
        check_encoding(args.target,False);check_encoding(args.intent,True)
        baseline=json.loads((HERE/'alat/kondisi_awal.json').read_text(encoding='utf-8'))
        unchanged=0;notebook_changes=[]
        for rel,digest in baseline['sha256'].items():
            actual=hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()
            if actual==digest: unchanged+=1
            elif Path(rel).suffix=='.ipynb':
                # Pemeriksaan dataset tidak bergantung pada output training notebook lain.
                # Pertahankan bukti perubahan eksternal; jangan menimpa baseline/notebook.
                notebook_changes.append(dict(path=rel,before=digest,current=actual))
            else: require(False,f'File sumber/alat asli berubah: {rel}')
        target,rows=validate_target(args.target)
        intent=validate_intent(args.intent)
        revision=validate_revision(rows,args.intent)
        report=dict(status='LULUS',target=target,intent=intent,notebook_loader=run_loader(args.target),
                    protected_files_unchanged=unchanged,notebook_changes_during_task=notebook_changes,revisi1=revision)
        print(json.dumps(report,ensure_ascii=False,indent=2))
    except (ValueError,KeyError,TypeError,FileNotFoundError,AssertionError) as exc:
        print(f'GAGAL: {exc}',file=sys.stderr);return 1
    return 0

if __name__=='__main__':sys.exit(main())
