import sys, json, importlib, ast, copy
from pathlib import Path
ROOT = Path(r'C:/Users/andyc/Documents/a_skripsi')
GAME = ROOT / 'Games/backend'
NB = ROOT / 'training/prethesis/ai_2_dataset_baru'
sys.path.insert(0, str(GAME))
sys.path.insert(1, str(ROOT / 'Games/tmp/profile-test-deps'))
from scripts import ekspor_otak_npc as ex
from services.npc_brain.generated import nlg
out = {}
expected = {r['modul']: r['sidik'] for r in json.loads((GAME/'services/npc_brain/generated/SUMBER.json').read_text())}
actual = ex.sidik_notebook(NB)
out['export_matches_notebooks'] = {k: actual[k] == expected[k] for k in expected}
contexts = {}
for method, filename, cells in [
    ('fuzzy','npc_fuzzy',[65,66,73,79,80,83]),
    ('utility','npc_utility_ai',[58,59,66,72,73,76]),
    ('bt','npc_behavior_tree',[62,63,70,76,77,80]),
]:
    mod = importlib.import_module('services.npc_brain.generated.otak_'+method)
    env = dict(vars(mod))
    env['tampilkan'] = lambda *a,**kw: None
    nb = json.loads((NB/(filename+'.ipynb')).read_text(encoding='utf-8'))
    checks=[]
    for i in cells:
        try:
            exec(compile(''.join(nb['cells'][i]['source']), filename+':cell'+str(i+1), 'exec'), env)
            checks.append({'cell':i+1,'ok':True})
        except Exception as e:
            checks.append({'cell':i+1,'ok':False,'error':str(e)})
    scenarios=env['hasil_skenario']
    out[method]={'notebook_checks':checks,'scenarios':len(scenarios),'scenario_failures':scenarios.loc[~scenarios.lulus].to_dict('records'),'check_groups':len(env['uji'])}
    contexts[method] = env
    # Existing anti-echo assertion checks candidate filtering, not selected action.
    result = env['putuskan'](env['ingatan_gema'], env['dasar_gag']['view'])
    out[method]['echo_repro'] = {'echo_count':result['konteks']['gema_tuduh'].get('Dodi'), 'decision':result['rencana_chat']}
    # All messages from same poll receive same time; UUID lexical order reverses chronology.
    common={'ronde':1,'fase':'day','waktu':20,'conf_intent':1.0}
    chats=[dict(common,id='z-first',pengirim='Andi',teks='Budi mencurigakan',intent='offend',target=[{'pemain':'Budi','relasi':'offend'}]),dict(common,id='a-second',pengirim='Budi',teks='Citra mencurigakan',intent='offend',target=[{'pemain':'Citra','relasi':'offend'}])]
    mem=env['buat_ingatan']([])
    mem.chat=copy.deepcopy(chats)
    view=env['buat_view'](1,'day',30)
    t,_=env['hitung_bukti'](mem,view)
    reversed_score=float(env['baris_pemain'](t,'Budi')['pengalihan'])
    mem.chat[0]['id']='a-first';mem.chat[1]['id']='z-second'
    t,_=env['hitung_bukti'](mem,view)
    ordered_score=float(env['baris_pemain'](t,'Budi')['pengalihan'])
    out[method]['uuid_changes_evidence']={'original_chronology_score':ordered_score,'reversed_uuid_score':reversed_score}
    # Last tribunal message arrives to bot in day of next round.
    mem=mod.Ingatan('Nara')
    s=env['_snapshot'](1,'tribunal')
    mem.sinkron_snapshot(s,100)
    s=env['_snapshot'](2,'day')
    s['messages']=[{'id':'late-tribunal','sender':'Andi','message':'Budi mencurigakan'}]
    mem.sinkron_snapshot(s,101)
    out[method]['late_chat_recorded_as']={k:mem.chat[-1][k] for k in ['ronde','fase','waktu']}
# Username may legally be pronoun/role. Exact match is checked before protected words.
out['name_collision'] = nlg.samarkan_nama('aku bukan hitman', ['Nara','aku','hitman'], 'hitman', 'Nara', frozenset())
p={'pembicara':'Nara','aksi':'tuduh','intent':'offend','target':'Budi','klaim':False,'bukti':['Budi dan Citra saling membela.']}
class StubNLU:
    def intent(self,*a): return 'offend',0.99
    def target(self,*a): return [{'pemain':'Budi','relasi':'offend'},{'pemain':'Citra','relasi':'offend'}]
k={'roster':['Nara','Budi','Citra'],'chat_terbaru':[]}
out['nlg_extra_target_accepted']=nlg.nilai_kalimat('Aku curiga Budi dan Citra.',p,k,StubNLU())
p2={**p,'target':'bot','bukti':[]}
out['nlg_unsafe_fallback']=nlg.tulis_pesan(p2,{'roster':['Nara','bot','Budi'],'chat_terbaru':[]},None,None)
Path(__file__).with_suffix('.json').write_text(json.dumps(out,ensure_ascii=False,indent=2,default=str),encoding='utf-8')
print(json.dumps(out,ensure_ascii=True,indent=2,default=str))
