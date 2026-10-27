import csv, hashlib, json
from collections import defaultdict
import label_target as lt

QUOTAS = dict.fromkeys(['ambiguous','witness','mixed_relations','reference_start','short_history_1','self'],50)
QUOTAS.update(dict.fromkeys(['second_person','plural_reference','rhetorical_question','agreement',
                           'multiple_targets','interruption','first_message_unknown','neutral_status'],25))
FOCUS = {
 'ambiguous':'Sedikitnya dua calon acuan dia sama kuat; nama terakhir bukan jawaban. Target tidak_diketahui.',
 'witness':'Nama sumber/saksi/penuduh bukan target. Sertakan bantahan isi klaim Peek penuduh yang membela pengirim saja.',
 'mixed_relations':'Bela A dan tuduh B; variasi urutan, kata ganti, dan pembelaan dalam anak kalimat.',
 'reference_start':'Tepat 12 konteks; nama target hanya pada konteks pertama; utama dia/-nya.',
 'short_history_1':'Satu konteks. Tepat 25 pembelaan diri setelah dituduh; penuduh bukan target. Sisanya offend/neutral.',
 'self':'Bela diri atau permintaan vote diri yang tulus; riwayat menyebut pemain lain sebagai pengalih.',
 'second_person':'Kamu/lu terikat pembicara jelas, termasuk bukan pengirim tepat sebelumnya.',
 'plural_reference':'Mereka/keduanya menunjuk dua orang. Sapaan ke pemain ketiga bukan target.',
 'rhetorical_question':'Pertanyaan retoris offend/defend mengacu pembicara terakhir.',
 'agreement':'Setuju/bantah tanpa ulang nama target; sumber pendapat bukan target.',
 'multiple_targets':'Dua pemain bernama dengan relasi sama.',
 'interruption':'Selingan waktu lalu kembali ke target; sertakan pembelaan diri.',
 'first_message_unknown':'Tanpa riwayat, dia/kamu tanpa acuan; roster minimal empat.',
 'neutral_status':'Neutral bertarget neutral: nama, kamu jelas, atau jawaban ke penanya khusus.',
}
LENGTHS = dict(ambiguous=3,witness=3,mixed_relations=3,reference_start=13,short_history_1=2,self=3,
 second_person=4,plural_reference=3,rhetorical_question=2,agreement=3,multiple_targets=2,
 interruption=4,first_message_unknown=1,neutral_status=2)

def labels_for(case,n):
    if case=='mixed_relations': return ['offend']*n
    if case=='neutral_status': return ['neutral']*n
    if case=='short_history_1':
        return ['defend' if i%2==0 else ('offend' if i%4==1 else 'neutral') for i in range(n)]
    return ['defend' if i%2==0 else 'offend' for i in range(n)]

def plan_additions(source,old_target,quota_file=None):
    quotas = json.loads(quota_file.read_text(encoding='utf-8')) if quota_file else QUOTAS
    if set(quotas)!=set(QUOTAS) or any(type(v)!=int or v<1 for v in quotas.values()):
        raise ValueError('Kuota wajib 14 kasus dan bilangan positif')
    old=list(csv.DictReader(old_target.open(encoding='utf-8-sig',newline='')))
    excluded={r['source_group'] for r in old}
    norm=lambda t:' '.join(t.casefold().split())
    old_text={norm(r['teks_chat']) for r in old}
    queues=defaultdict(list)
    seen=set(excluded)
    for row in sorted(lt.read_source(source),key=lambda r:hashlib.sha256(('tambahan03'+r['source_group']).encode()).hexdigest()):
        if row['source_group'] in seen or norm(row['teks_chat']) in old_text: continue
        seen.add(row['source_group'])
        queues[row['label_intent']].append(row)
    jobs=[]
    for case,n in quotas.items():
        for index,label in enumerate(labels_for(case,n)):
            if not queues[label]: raise ValueError('Sumber bebas kebocoran tidak cukup')
            row=queues[label].pop()
            jobs.append(dict(job_id=f"r{row['source_row']:06d}_v02",case_name=case,
                case_description=lt.CASES[case]+' FOKUS TAMBAHAN: '+FOCUS[case],source=row,
                context_limit=12,jumlah_pesan=LENGTHS[case],pesan_typo_ringan=[],case_index=index))
    return jobs
