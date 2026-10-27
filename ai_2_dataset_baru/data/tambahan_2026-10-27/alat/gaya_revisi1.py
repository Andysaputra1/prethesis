"""Ukuran gaya Revisi 1. Definisi/tokenisasi sama untuk data lama dan baru."""
import re
from collections import Counter

MARKERS=('sih','kok','dong','nih')
def normalize(text):return ' '.join(text.casefold().split())
def words(text):return re.findall(r'\b\w+\b',text.casefold())

# Bela/membela yang benar-benar merupakan ujaran pemain tetap boleh.
# Yang dilarang: istilah anotasi dan instruksi yang menamai label pesan sendiri.
HIDDEN_LABEL=re.compile(
    r'\b(?:offend|defend|neutral|anotasi|dataset|label(?:nya)?|relasi)\b'
    r'|\b(?:catat\w*|tulis\w*|masukkan|simpan)\b.{0,35}\b(?:pembelaan|bela|membela)\b'
    r'|\b(?:tolong\s+)?(?:catat\w*\s+)?pembelaan\s+ini\b'
    r'|\b(?:pesan|kalimat)\s+(?:ini\s+)?(?:termasuk|berjenis|berkategori|berintent)\b',re.I)

def metrics(rows,intent):
    contexts=[m['teks_chat'] for r in rows for m in r['chat_sebelumnya']]
    texts=contexts+[r['teks_chat'] for r in rows]
    occurrences=Counter(normalize(t) for t in contexts)
    tokens=Counter(words(' '.join(texts)));total=sum(tokens.values())
    catat=[i+2 for i,r in enumerate(intent) if re.search(r'catat',r['teks_chat'],re.I)]
    bela=[i+2 for i,r in enumerate(intent) if re.search(r'\b(?:bela|pembelaan|membela)\b',r['teks_chat'],re.I)]
    hidden=[t for t in texts+[r['teks_chat'] for r in intent] if HIDDEN_LABEL.search(t)]
    return dict(context_messages=len(contexts),unique_contexts=len(occurrences),
        unique_context_ratio=len(occurrences)/len(contexts) if contexts else 0,
        max_context_reuse=max(occurrences.values(),default=0),word_count=total,
        catatan_per_1000=tokens['catatan']*1000/total if total else 0,
        marker_per_1000={w:tokens[w]*1000/total if total else 0 for w in MARKERS},
        intent_catat_rows=catat,intent_bela_rows=bela,intent_bela_ratio=len(bela)/len(intent) if intent else 0,
        hidden_label_texts=hidden)

def validate_style(rows,intent,old_rows,old_intent):
    new=metrics(rows,intent);old=metrics(old_rows,old_intent)
    errors=[]
    if new['unique_context_ratio']<.95:errors.append('Konteks unik harus >=95%')
    if new['max_context_reuse']>2:errors.append('Satu teks konteks maksimal 2x')
    if new['catatan_per_1000']>1:errors.append('catatan harus <=1 per 1.000 kata')
    for marker in MARKERS:
        if new['marker_per_1000'][marker]<old['marker_per_1000'][marker]/2:
            errors.append(f'Penanda {marker} kurang dari separuh frekuensi data lama')
    if new['intent_catat_rows']:errors.append('Intent tambahan tidak boleh memuat catat')
    if new['intent_bela_ratio']>.03:errors.append('Intent bela/pembelaan/membela harus <=3%')
    if new['hidden_label_texts']:errors.append('Ditemukan kata label terselubung/instruksi anotasi')
    if errors:raise ValueError('; '.join(errors))
    return dict(current=new,old=old,thresholds=dict(unique_context_ratio=.95,max_context_reuse=2,
        catatan_per_1000=1,marker_per_1000={w:old['marker_per_1000'][w]/2 for w in MARKERS},
        intent_catat_rows=0,intent_bela_ratio=.03,hidden_label_texts=0))
