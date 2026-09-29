"""Alur manual lewat ChatGPT/Gemini (web) tanpa API.

1. prompts: tulis prompt per batch ke <folder>/prompt/prompt_XXX.txt.
2. Tempel satu prompt ke ChatGPT atau Gemini, lalu simpan seluruh jawabannya sebagai
   <folder>/hasil/XXX_<model>.txt, misalnya hasil/001_gemini.txt atau hasil/001_chatgpt.txt.
3. import: validasi semua jawaban. Yang lolos disimpan di <folder>/sessions; yang gagal
   dibuatkan prompt ulang di <folder>/prompt_ulang beserta alasan gagalnya.
4. export: tulis CSV enam kolom dari semua sesi yang lolos.
"""

import argparse
import json
import re
import shutil
from collections import Counter
from pathlib import Path

import label_target as lt


MANUAL_RULES = lt.GENERATION_INSTRUCTIONS + """
Setiap job berdiri sendiri; sumber antar-job bukan riwayat percakapan bersama.
Nomor bukti_pesan dimulai ulang dari 1 di setiap session.
focus_player harus nama peserta atau string kosong; tidak_diketahui bukan peserta.
Untuk kasus posisi acuan, pesan utama tidak menyebut ulang nama focus_player.
Untuk memori di luar jendela, gunakan rantai bukti pada pesan yang masih terlihat.
Untuk acuan yang sudah hilang, jangan memasukkan target lama pada anotasi konteks.

FORMAT JAWABAN (WAJIB):
- Balas HANYA dengan satu blok kode json berisi {"results": [...]}, tanpa penjelasan lain.
- Satu item per job: {"job_id", "session": {"case_name", "participants", "focus_player",
  "panggilan", "messages"}}. Setiap pesan: {"pengirim", "teks_chat", "label_intent",
  "target": [{"pemain", "relasi", "bukti_pesan"}]}. panggilan: [{"pemain", "sebutan": [...]}] atau [].
- Salin job_id dan case_name persis. Jumlah pesan harus sama dengan jumlah_pesan.
- Pesan TERAKHIR adalah contoh utama; label_intent-nya sama dengan source.label_intent.
- bukti_pesan berisi nomor pesan yang menyebut nama target (atau yang anotasinya memuat
  target), paling jauh 12 pesan sebelumnya dan tidak pernah pesan sesudahnya.
  Target tidak_diketahui selalu memakai bukti_pesan [].
- Selesaikan SEMUA job; jangan memotong JSON di tengah.

Contoh bentuk jawaban (bukan data sungguhan):
```json
{"results": [{"job_id": "r000123_v01", "session": {"case_name": "explicit",
 "participants": ["Andi", "Budi"], "focus_player": "Andi", "panggilan": [],
 "messages": [{"pengirim": "Budi", "teks_chat": "Aku curiga Andi, alibinya berubah terus.",
 "label_intent": "offend", "target": [{"pemain": "Andi", "relasi": "offend", "bukti_pesan": [1]}]}]}}]}
```
"""


def write_prompt(path, jobs, errors=None):
    payload = {"jobs": [lt.job_for_model(job) for job in jobs]}
    if errors:
        payload["kesalahan_sebelumnya"] = errors
    path.write_text(MANUAL_RULES + "\nJOBS:\n" + json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")


# Jawaban web biasanya dibungkus blok kode; ambil isi JSON-nya saja.
def extract_json(text):
    match = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.S)
    raw = match.group(1) if match else text[text.find("{"):text.rfind("}") + 1]
    return json.loads(raw)


def load_jobs(folder):
    return json.loads((folder / "jobs.json").read_text(encoding="utf-8"))


def cmd_prompts(args):
    folder = args.dir.resolve()
    if (folder / "jobs.json").exists():
        raise SystemExit(f"{folder} sudah berisi jobs.json; pakai folder baru agar hasil lama tidak tertimpa.")
    jobs = lt.plan_jobs(lt.read_source(args.input), 1)
    if args.per_case:
        jobs = lt.select_per_case(jobs, args.per_case)
    (folder / "prompt").mkdir(parents=True)
    (folder / "hasil").mkdir()
    (folder / "jobs.json").write_text(json.dumps(jobs, ensure_ascii=False, indent=1), encoding="utf-8")
    batches = [jobs[i:i + args.batch_size] for i in range(0, len(jobs), args.batch_size)]
    for number, batch in enumerate(batches, start=1):
        write_prompt(folder / "prompt" / f"prompt_{number:03d}.txt", batch)
    print(f"{len(jobs)} job dalam {len(batches)} prompt di {folder / 'prompt'}")


def cmd_import(args):
    folder = args.dir.resolve()
    jobs = {job["job_id"]: job for job in load_jobs(folder)}
    sessions = folder / "sessions"
    sessions.mkdir(exist_ok=True)
    batch_result, _ = lt.build_schemas()
    errors, attempted, notes = {}, set(), []
    per_model = Counter()
    for file in sorted((folder / "hasil").glob("*.*")):
        model = file.stem.split("_", 1)[1] if "_" in file.stem else "tanpa_nama"
        try:
            payload = extract_json(file.read_text(encoding="utf-8"))
            items = payload["results"]
        except (ValueError, KeyError, TypeError):
            notes.append(f"- {file.name}: JSON tidak terbaca (jawaban terpotong atau ada teks tambahan).")
            continue
        for raw in items:
            job_id = raw.get("job_id") if isinstance(raw, dict) else None
            if job_id not in jobs:
                notes.append(f"- {file.name}: job_id tidak dikenal {job_id!r}.")
                continue
            attempted.add(job_id)
            checkpoint = sessions / f"{job_id}.json"
            if checkpoint.exists():
                continue
            try:
                item = batch_result.model_validate({"results": [raw]}).results[0].model_dump()
                lt.validate_session(item["session"], jobs[job_id])
            except (ValueError, KeyError, TypeError) as exc:
                errors[job_id] = str(exc).splitlines()[0][:300]
                per_model[(model, "gagal")] += 1
                continue
            checkpoint.write_text(json.dumps({
                "job": jobs[job_id], "session": item["session"], "model_verification_passed": False,
                "generation_settings": {"provider": "manual_web", "model": model, "source_file": file.name},
            }, ensure_ascii=False, indent=2), encoding="utf-8")
            errors.pop(job_id, None)
            per_model[(model, "lolos")] += 1

    accepted = {p.stem for p in sessions.glob("*.json")}
    failed = [jobs[j] for j in jobs if j in attempted and j not in accepted]
    retry = folder / "prompt_ulang"
    shutil.rmtree(retry, ignore_errors=True)
    if failed:
        retry.mkdir()
        for number in range(0, len(failed), args.batch_size):
            batch = failed[number:number + args.batch_size]
            write_prompt(retry / f"ulang_{number // args.batch_size + 1:03d}.txt", batch,
                         {job["job_id"]: errors.get(job["job_id"], "Belum lolos pemeriksaan.") for job in batch})

    cases = Counter(jobs[j]["case_name"] for j in accepted)
    models = sorted({m for m, _ in per_model})
    lines = ["# Laporan impor", "",
             f"- Lolos: {len(accepted)} dari {len(jobs)} job",
             f"- Gagal dan perlu diulang: {len(failed)} (prompt di prompt_ulang/)",
             f"- Belum pernah dikerjakan: {len(jobs) - len(attempted | accepted)}", "",
             "## Per model", ""]
    lines += [f"- {m}: {per_model[(m, 'lolos')]} lolos, {per_model[(m, 'gagal')]} gagal" for m in models] or ["- (belum ada)"]
    lines += ["", "## Lolos per kasus", ""] + [f"- {case}: {cases[case]}" for case in lt.CASES if cases[case]]
    lines += ["", "## Gagal", ""] + [f"- {j} ({jobs[j]['case_name']}): {errors.get(j, '-')}" for j in sorted(errors)]
    if notes:
        lines += ["", "## Catatan file", ""] + notes
    (folder / "laporan.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Lolos {len(accepted)}/{len(jobs)} | gagal {len(failed)} | lihat {folder / 'laporan.md'}")


def cmd_export(args):
    folder = args.dir.resolve()
    items = []
    for job in load_jobs(folder):
        path = folder / "sessions" / f"{job['job_id']}.json"
        if path.exists():
            items.append(json.loads(path.read_text(encoding="utf-8")))
    output = args.output.resolve()
    lt.export_records(items, output, output.with_suffix(".groups.jsonl"))
    print(f"{len(items)} baris ditulis ke {output}")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    prompts = sub.add_parser("prompts", help="Buat file prompt per batch")
    prompts.add_argument("--input", type=Path, default=lt.PROJECT_ROOT / "ai_2_dataset_baru/data/dataset_final3.csv")
    prompts.add_argument("--dir", type=Path, required=True)
    prompts.add_argument("--per-case", type=int)
    prompts.add_argument("--batch-size", type=int, default=10)
    imported = sub.add_parser("import", help="Validasi jawaban di folder hasil/")
    imported.add_argument("--dir", type=Path, required=True)
    imported.add_argument("--batch-size", type=int, default=10)
    exported = sub.add_parser("export", help="Tulis CSV dari sesi yang lolos")
    exported.add_argument("--dir", type=Path, required=True)
    exported.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    {"prompts": cmd_prompts, "import": cmd_import, "export": cmd_export}[args.command](args)


if __name__ == "__main__":
    main()
