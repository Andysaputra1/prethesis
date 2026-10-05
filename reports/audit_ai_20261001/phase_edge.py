import sys,json,random
from pathlib import Path
ROOT=Path(r'C:/Users/andyc/Documents/a_skripsi')
sys.path.insert(0,str(ROOT/'Games/backend'))
from services.match_engine import Match
from services.npc_brain.generated import otak_bt as m
names=['Nara','Andi','Budi','Citra','Dodi','Eka']
g=Match(names,[],now=0,rng=random.Random(9))
for p,r in zip(names,['civilian','civilian','civilian','spy','hitman','stalker']):g.players[p].role=r
g.phase='tribunal';g.deadline=100
mem=m.Ingatan('Nara')
mem.sinkron_snapshot(g.snapshot('Nara'),98)
# Public events arrive after bot's last poll and before the phase deadline.
msg=g.add_message('Andi','Budi mencurigakan')
g.vote('Andi','Budi'); g.vote('Nara','Budi')
g.tick(100)
mem.sinkron_snapshot(g.snapshot('Nara'),101)
out={'engine_phase':[g.round,g.phase], 'message_in_engine':msg,'bot_message_memory':mem.chat,'bot_vote_memory':mem.vote,'bot_execution_memory':mem.eksekusi}
Path(__file__).with_suffix('.json').write_text(json.dumps(out,indent=2),encoding='utf8');print(json.dumps(out,indent=2))
