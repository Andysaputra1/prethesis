"""Salin pipeline manual; hanya menulis di direktori tambahan."""
from pathlib import Path
import hashlib, json, subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
DATA = ROOT / 'ai_2_dataset_baru/data'
protected = [DATA/'dataset_final3.csv', DATA/'dataset_final3_context_target_pilot25_lengkap.csv',
             DATA/'ATURAN_LABEL.md', *sorted((ROOT/'ai_2_dataset_baru').glob('*.ipynb')),
             ROOT/'lama/generateDataset/label_target.py', ROOT/'lama/generateDataset/label_target_manual.py']
manifest = HERE/'kondisi_awal.json'
if not manifest.exists():
    manifest.write_text(json.dumps({'git_status': subprocess.check_output(['git','status','--short'],cwd=ROOT,text=True),
        'sha256': {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}},indent=2),encoding='utf-8')

s = (ROOT/'lama/generateDataset/label_target.py').read_text(encoding='utf-8')
s = s.replace('Path(__file__).resolve().parents[2]', 'Path(__file__).resolve().parents[4]')
s = s.replace('Relasi tiap target offend atau defend,', 'Relasi target non-neutral offend atau defend,')
s = s.replace('"offend", "defend"]\n        bukti_pesan', '"offend", "defend", "neutral"]\n        bukti_pesan')
s = s.replace('if (label == "neutral" and relations) or (label != "neutral" and not relations):\n            raise ValueError("Neutral harus target kosong; non-neutral harus punya relasi.")',
'''if label == "neutral" and any(r["relasi"] != "neutral" for r in relations):
            raise ValueError("Target neutral hanya boleh berelasi neutral.")
        if label != "neutral" and (not relations or any(r["relasi"] == "neutral" for r in relations)):
            raise ValueError("Non-neutral wajib bertarget tanpa relasi neutral.")''')
s = s.replace('if relation["relasi"] not in {"offend", "defend"}:', 'if relation["relasi"] not in {"offend", "defend", "neutral"}:')
s = s.replace('  atau diajak di-vote. Meragukan klaim, mengkritik cara diskusi, atau menolak tuduhan\n  bukan offend; jangan menambah offend ke penuduh hanya karena ia dibantah.',
'''  atau diajak di-vote. Menyerang kredibilitas, motif, perilaku atau konsistensi penuduh
  adalah offend (O-c); kritik isi tuduhan tanpa menyerang penuduh adalah defend (D-d).''')
s = s.replace('- Neutral: target=[]; nama yang disapa bukan otomatis target.', '- Neutral: target berelasi neutral untuk nama/acuan/sapaan jelas atau penanya yang dijawab; selain itu [].')
s = s.replace('target kosong.', 'target neutral sesuai ATURAN_LABEL.md.')
s = s.replace('target kosong;','target neutral sesuai ATURAN_LABEL.md;')
start=s.index('Gunakan bahasa santai dengan ejaan jelas:')
end=s.index('Setiap balasan harus nyambung',start)
s=s[:start]+'''Gunakan variasi bahasa pemain Indonesia: aku/gw/gue, ejaan jelas maupun singkatan wajar.
Ikuti jumlah_pesan persis. Jangan merusak nama, negasi, atau acuan.
'''+s[end:]
start=s.index('    with output.open("x",',s.index('def export_records('))
end=s.index('\n\n# Default hanya preview',start)
s=s[:start]+'''    fields = FIELDS + ["session_id", "case_name", "source_group", "source_csv_row",
                       "synthetic_context", "panggilan", "direvisi"]
    with output.open("x", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\\r\\n")
        writer.writeheader()
        for item in accepted:
            session, job = item["session"], item["job"]
            validate_session(session, job)
            record = make_record(session)
            record.update(session_id=job["job_id"], case_name=job["case_name"],
                          source_group=job["source"]["source_group"], source_csv_row=job["source"]["source_row"],
                          synthetic_context=True, panggilan=session.get("panggilan", []), direvisi=False)
            for field in ["chat_sebelumnya", "daftar_pemain", "target", "panggilan"]:
                record[field] = json.dumps(record[field], ensure_ascii=False, separators=(",", ":"))
            writer.writerow(record)
''' + s[end:]
insert='''
# Aturan resmi mengalahkan instruksi generasi historis.
GENERATION_INSTRUCTIONS += "\\nATURAN LABEL RESMI:\\n" + (PROJECT_ROOT / "ai_2_dataset_baru/data/ATURAN_LABEL.md").read_text(encoding="utf-8")
VERIFICATION_INSTRUCTIONS += "\\n" + (PROJECT_ROOT / "ai_2_dataset_baru/data/ATURAN_LABEL.md").read_text(encoding="utf-8")

'''
s=s.replace('\ndef job_for_model(job):',insert+'\ndef job_for_model(job):')
(HERE/'label_target.py').write_text(s,encoding='utf-8')
s=(ROOT/'lama/generateDataset/label_target_manual.py').read_text(encoding='utf-8')
s=s.replace('import label_target as lt','import label_target as lt\nfrom rencana import plan_additions')
s=s.replace('jobs = lt.plan_jobs(lt.read_source(args.input), 1)\n    if args.per_case:\n        jobs = lt.select_per_case(jobs, args.per_case)',
'''jobs = plan_additions(args.input, args.old_target, args.quotas)''')
s=s.replace('shutil.rmtree(retry, ignore_errors=True)', '''# Hanya hapus prompt ulang milik folder kerja yang sudah di-resolve.
    if retry.resolve().parent != folder or retry.is_symlink():
        raise ValueError("Direktori retry di luar folder kerja")
    retry.mkdir(exist_ok=True)
    for stale in retry.glob("ulang_*.txt"):
        stale.unlink()''')
s=s.replace('        retry.mkdir()','        retry.mkdir(exist_ok=True)')
s=s.replace('(folder / "laporan.md")', '(folder / "alat" / "laporan_impor.md")')
s=s.replace("{folder / 'laporan.md'}", "{folder / 'alat' / 'laporan_impor.md'}")
s=s.replace('    output = args.output.resolve()', '''    if len(items) != len(load_jobs(folder)):
        raise ValueError("Export menolak job yang belum lengkap")
    output = args.output.resolve()''')
s=s.replace('    prompts.add_argument("--per-case", type=int)', '''    prompts.add_argument("--quotas", type=Path, help="JSON kuota; default plan03 (500 sesi)")
    prompts.add_argument("--old-target", type=Path, default=lt.PROJECT_ROOT / "ai_2_dataset_baru/data/dataset_final3_context_target_pilot25_lengkap.csv")''')
(HERE/'label_target_manual.py').write_text(s,encoding='utf-8')
print('Salinan pipeline dan hash kondisi awal siap')
