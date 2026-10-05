import sys,json,time,hashlib
from pathlib import Path
ROOT=Path(r'C:/Users/andyc/Documents/a_skripsi')
sys.path.insert(0,str(ROOT/'Games/backend'))
from services.npc_brain.generated.nlg import NLUIndoBERT,anotasi_chat
import torch
torch.set_num_threads(2)
start=time.perf_counter()
model=NLUIndoBERT(ROOT/'Games/backend/artifacts/indobert/intent',ROOT/'Games/backend/artifacts/indobert/target','cpu')
load=time.perf_counter()-start
roster=['Nara','Andi','Budi','Citra','Dodi','Eka']
samples=[('Andi','Aku curiga Budi itu Hitman.'),('Budi','Aku bukan Hitman, jangan asal tuduh.'),('Citra','Menurutku Budi bukan Hitman.'),('Eka','Ada yang punya info?'),('Andi','Budi mencurigakan, tapi Citra bukan Hitman.')]
rows=[]
for sender,text in samples:
    t=time.perf_counter();r=anotasi_chat(model,{'pengirim':sender,'teks':text},[],roster)
    rows.append({**r,'seconds':round(time.perf_counter()-t,3)})
# Compare deployed artifact to training source, including actual weights.
comparisons={}
for kind,folder in [('intent','models/notebook_standalone/intent_classifier_transformer'),('target','models/target_classifier/target_classifier_transformer')]:
    a=ROOT/'Games/backend/artifacts/indobert'/kind;b=ROOT/'training/prethesis/ai_2_dataset_baru'/folder
    def digest(p):
        if not p.exists(): return None
        with p.open('rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()
    comparisons[kind]={name:digest(a/name)==digest(b/name) for name in ['model.safetensors','config.json','tokenizer.json']}
out={'load_seconds':load,'smoke':rows,'artifacts_match_training':comparisons}
Path(__file__).with_suffix('.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(out,ensure_ascii=True,indent=2))
