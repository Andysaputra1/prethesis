"""Uji negatif bermakna: data rusak wajib ditolak; hanya memakai salinan sementara."""
import copy,csv,json,sys,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE))
import cek_tambahan as ck

class CheckerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.header,cls.rows=ck.read_csv(HERE.parent/'dataset_target_tambahan.csv')
        _,cls.old=ck.read_csv(HERE.parent/'dataset_final3_context_target_pilot25_lengkap.csv')
        cls.path=HERE/'alat'/'_uji_target_sementara.csv'
        if cls.path.exists():raise RuntimeError('File sementara sudah ada; tidak ditimpa')
    @classmethod
    def tearDownClass(cls):
        if cls.path.exists():cls.path.unlink()
    def reject(self,change,match):
        rows=copy.deepcopy(self.rows);header=self.header.copy();change(rows,header)
        with self.path.open('w',encoding='utf-8',newline='') as h:
            writer=csv.DictWriter(h,fieldnames=header,lineterminator='\r\n');writer.writeheader();writer.writerows(rows)
        with self.assertRaisesRegex(ValueError,match):ck.validate_target(self.path)
    def case(self,rows,case):return next(r for r in rows if r['case_name']==case)
    def test_header_order(self):self.reject(lambda r,h:h.reverse(),'Header')
    def test_duplicate_id(self):self.reject(lambda r,h:r[1].update(session_id=r[0]['session_id']),'duplikat')
    def test_old_id(self):self.reject(lambda r,h:r[0].update(session_id=self.old[0]['session_id']),'session_id bocor')
    def test_source_leak(self):self.reject(lambda r,h:r[0].update(source_group=self.old[0]['source_group']),'source_group bocor')
    def test_quota(self):
        def change(r,h):
            for x in r[:3]:x['case_name']='self'
        self.reject(change,'Kuota')
    def test_bad_json(self):self.reject(lambda r,h:r[0].update(target='['),'Expecting')
    def test_history_sender(self):
        def change(r,h):
            hist=json.loads(r[0]['chat_sebelumnya']);hist[0]['pengirim']='DiLuarRoster'
            r[0]['chat_sebelumnya']=json.dumps(hist,ensure_ascii=False,separators=(',',':'))
        self.reject(change,'konteks 1: pengirim')
    def test_unknown_case(self):
        def change(r,h):
            x=self.case(r,'ambiguous');x['target']=json.dumps([dict(pemain=x['pengirim'],relasi=x['label_intent'])],separators=(',',':'))
        self.reject(change,'unknown wajib')
    def test_mixed(self):
        def change(r,h):
            x=self.case(r,'mixed_relations');x['target']=json.dumps([t for t in json.loads(x['target']) if t['relasi']=='offend'],separators=(',',':'))
        self.reject(change,'campuran tidak lengkap')
    def test_reference_count(self):
        def change(r,h):
            x=self.case(r,'reference_start');x['chat_sebelumnya']=json.dumps(json.loads(x['chat_sebelumnya'])[:-1],separators=(',',':'))
        self.reject(change,'wajib 12 konteks')
    def test_short_count(self):
        def change(r,h):
            x=self.case(r,'short_history_1');x['chat_sebelumnya']=json.dumps(json.loads(x['chat_sebelumnya'])*2,separators=(',',':'))
        self.reject(change,'wajib satu konteks')
    def test_self(self):
        def change(r,h):
            x=self.case(r,'self');other=next(p for p in json.loads(x['daftar_pemain']) if p!=x['pengirim'])
            x['target']=json.dumps([dict(pemain=other,relasi=x['label_intent'])],separators=(',',':'))
        self.reject(change,'self bukan pengirim')
    def test_duplicate_old_text(self):self.reject(lambda r,h:r[0].update(teks_chat=self.old[0]['teks_chat']),'identik pesan lama')
    def test_neutral_accepted(self):
        ck.check_message(dict(pengirim='Sekar',teks_chat='Kirana, role apa?',label_intent='neutral',target=[dict(pemain='Kirana',relasi='neutral')]),{'Sekar','Kirana'},'uji')
    def test_neutral_wrong_relation(self):
        with self.assertRaisesRegex(ValueError,'neutral harus'):
            ck.check_message(dict(pengirim='Sekar',teks_chat='Kirana role apa?',label_intent='neutral',target=[dict(pemain='Kirana',relasi='defend')]),{'Sekar','Kirana'},'uji')
    def test_non_neutral_empty(self):
        with self.assertRaisesRegex(ValueError,'non-neutral'):
            ck.check_message(dict(pengirim='Sekar',teks_chat='aku bukan Hitman',label_intent='defend',target=[]),{'Sekar'},'uji')
    def test_non_neutral_neutral_relation(self):
        with self.assertRaisesRegex(ValueError,'non-neutral'):
            ck.check_message(dict(pengirim='Sekar',teks_chat='aku bukan Hitman',label_intent='defend',target=[dict(pemain='Sekar',relasi='neutral')]),{'Sekar'},'uji')
    def test_offend_priority(self):
        with self.assertRaisesRegex(ValueError,'diutamakan'):
            ck.check_message(dict(pengirim='Sekar',teks_chat='aku aman, Kirana sus',label_intent='defend',target=[dict(pemain='Sekar',relasi='defend'),dict(pemain='Kirana',relasi='offend')]),{'Sekar','Kirana'},'uji')
    def test_unknown_player(self):
        with self.assertRaisesRegex(ValueError,'target di luar'):
            ck.check_message(dict(pengirim='Sekar',teks_chat='Kirana sus',label_intent='offend',target=[dict(pemain='Kirana',relasi='offend')]),{'Sekar'},'uji')
    def test_similar(self):
        found=ck.similar_pairs(['Aku bukan Hitman dan tidak melakukan Hostage malam ini.',
                               'aku bukan hitman dan tidak melakukan hostage malam ini!',
                               'aku bukan hitman dan tidak melakukan Hostage malam itu.'])
        self.assertEqual(len(found),3)
    def test_exact_notebook_loader(self):
        report=ck.run_loader(HERE.parent/'dataset_target_tambahan.csv')
        self.assertEqual(report['rows'],500)
    def test_intent_composition(self):
        header,rows=ck.read_csv(HERE.parent/'dataset_intent_tambahan.csv')
        rows[0]['label_intent']='neutral'
        with self.path.open('w',encoding='utf-8-sig',newline='') as h:
            w=csv.DictWriter(h,fieldnames=header,lineterminator='\r\n');w.writeheader();w.writerows(rows)
        with self.assertRaisesRegex(ValueError,'Komposisi label'):ck.validate_intent(self.path)
    def test_intent_duplicate(self):
        header,rows=ck.read_csv(HERE.parent/'dataset_intent_tambahan.csv');rows[1]=rows[0].copy()
        with self.path.open('w',encoding='utf-8-sig',newline='') as h:
            w=csv.DictWriter(h,fieldnames=header,lineterminator='\r\n');w.writeheader();w.writerows(rows)
        with self.assertRaisesRegex(ValueError,'Duplikat intent'):ck.validate_intent(self.path)

class RevisionStyleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from gaya_revisi1 import validate_style
        cls.validate=staticmethod(validate_style)
        _,cls.rows=ck.read_csv(HERE.parent/'dataset_target_tambahan.csv')
        _,cls.old=ck.read_csv(HERE.parent/'dataset_final3_context_target_pilot25_lengkap.csv')
        for row in cls.rows+cls.old:
            for key in ['chat_sebelumnya','daftar_pemain','target','panggilan']:row[key]=json.loads(row[key])
        _,cls.intent=ck.read_csv(HERE.parent/'dataset_intent_tambahan.csv')
        _,cls.old_intent=ck.read_csv(HERE.parent/'dataset_final3.csv')
    def validate_copy(self,rows=None,intent=None):
        return self.validate(rows if rows is not None else self.rows,intent if intent is not None else self.intent,self.old,self.old_intent)
    def test_revised_style_passes(self):self.assertEqual(self.validate_copy()['current']['unique_context_ratio'],1)
    def test_context_uniqueness_rejected(self):
        rows=copy.deepcopy(self.rows)
        for r in rows[:90]:r['chat_sebelumnya'][0]['teks_chat']='sekarang obrolan grup masih berjalan'
        with self.assertRaisesRegex(ValueError,'Konteks unik'):self.validate_copy(rows)
    def test_context_third_use_rejected(self):
        rows=copy.deepcopy(self.rows)
        for r in rows[:3]:r['chat_sebelumnya'][0]['teks_chat']='diskusi grup belum selesai nih'
        with self.assertRaisesRegex(ValueError,'maksimal 2x'):self.validate_copy(rows)
    def test_catatan_rate_rejected(self):
        rows=copy.deepcopy(self.rows);rows[0]['chat_sebelumnya'][0]['teks_chat']+=' catatan'*50
        with self.assertRaisesRegex(ValueError,'catatan harus'):self.validate_copy(rows)
    def test_each_marker_required(self):
        import re
        for marker in ['sih','kok','dong','nih']:
            with self.subTest(marker=marker):
                rows=copy.deepcopy(self.rows)
                for r in rows:
                    for m in [r,*r['chat_sebelumnya']]:m['teks_chat']=re.sub(r'\b'+marker+r'\b','',m['teks_chat'],flags=re.I)
                with self.assertRaisesRegex(ValueError,'Penanda '+marker):self.validate_copy(rows)
    def test_intent_catat_rejected(self):
        intent=copy.deepcopy(self.intent);intent[0]['teks_chat']+=' tolong dicatat'
        with self.assertRaisesRegex(ValueError,'tidak boleh memuat catat'):self.validate_copy(intent=intent)
    def test_intent_four_bela_rejected(self):
        intent=copy.deepcopy(self.intent)
        for r in intent[:4]:r['teks_chat']+=' aku bela dia'
        with self.assertRaisesRegex(ValueError,'harus <=3%'):self.validate_copy(intent=intent)
    def test_intent_three_bela_allowed(self):
        intent=copy.deepcopy(self.intent)
        for r in intent[:3]:r['teks_chat']+=' aku bela dia'
        self.assertEqual(self.validate_copy(intent=intent)['current']['intent_bela_ratio'],.03)
    def test_hidden_label_rejected(self):
        rows=copy.deepcopy(self.rows);rows[0]['chat_sebelumnya'][0]['teks_chat']+=' labelnya neutral'
        with self.assertRaisesRegex(ValueError,'label terselubung'):self.validate_copy(rows)
    def test_hidden_defense_instruction_rejected(self):
        intent=copy.deepcopy(self.intent);intent[0]['teks_chat']+=' tolong catat pembelaan ini'
        with self.assertRaisesRegex(ValueError,'label terselubung'):self.validate_copy(intent=intent)
    def test_frozen_annotation_rejected(self):
        from unittest.mock import patch
        original_read=Path.read_text
        first=HERE/'sessions'/f"{self.rows[0]['session_id']}.json"
        def changed_read(path,*args,**kwargs):
            raw=original_read(path,*args,**kwargs)
            if path==first:
                item=json.loads(raw);item['session']['messages'][0]['pengirim']=item['session']['messages'][-1]['pengirim']
                return json.dumps(item)
            return raw
        with patch.object(Path,'read_text',changed_read):
            with self.assertRaisesRegex(ValueError,'pengirim/label/target/bukti berubah'):
                ck.validate_revision(self.rows,HERE.parent/'dataset_intent_tambahan.csv')

if __name__=='__main__':unittest.main(verbosity=2)
