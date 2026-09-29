"""One Bedrock Haiku trial: at most ONE generation request, no model verifier/retries.
Default is an offline dry run. Uses existing source/job planning and local validation.
"""
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import json
import os
from pathlib import Path
import re
import sys
from typing import Literal
from urllib.parse import quote

from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict, ValidationError
import label_target as base

MODEL_ID = "global.anthropic.claude-haiku-4-5-20251001-v1:0"
PRICE_INPUT = Decimal("1")
PRICE_OUTPUT = Decimal("5")
PRICE_SOURCE = "https://platform.claude.com/docs/en/about-claude/pricing"

class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

class Relation(StrictModel):
    pemain: str
    relasi: Literal["offend", "defend"]
    bukti_pesan: list[int]

class Message(StrictModel):
    pengirim: str
    teks_chat: str
    label_intent: Literal["offend", "defend", "neutral"]
    target: list[Relation]

class Alias(StrictModel):
    pemain: str
    sebutan: list[str]

class Session(StrictModel):
    case_name: str
    participants: list[str]
    focus_player: str
    panggilan: list[Alias]
    messages: list[Message]

class Item(StrictModel):
    job_id: str
    session: Session

class Batch(StrictModel):
    results: list[Item]

# These instructions augment, rather than replace, the existing game/context rules.
PROMPT = base.GENERATION_INSTRUCTIONS + """

Definisi intent ada di atas. Kutipan bukan otomatis sikap pengirim.

Setiap job berdiri sendiri. Sumber antar-job bukan riwayat percakapan bersama.
Salin job_id persis; keluarkan tepat satu results item per job tanpa duplikat.
Urutan output boleh mengikuti input. Kembalikan JSON saja sesuai schema,
ringkas tanpa Markdown, komentar, atau penjelasan tambahan di luar schema.
Buat jumlah_pesan PERSIS; tidak perlu memperpanjang kalimat untuk memenuhi kuota.
Nomor bukti_pesan dimulai ulang dari 1 di setiap session.
focus_player harus nama peserta atau string kosong; tidak_diketahui bukan peserta.
Untuk kasus posisi acuan, pesan utama tidak menyebut ulang nama focus_player.
Untuk memori di luar jendela, gunakan rantai bukti pada pesan yang masih terlihat.
Untuk acuan yang sudah hilang, jangan memasukkan target lama pada anotasi konteks.
Pemeriksaan internal sebelum mengembalikan hasil: cocokkan ID, jumlah pesan,
intent utama dengan sumber, target neutral kosong, dan bukti tidak menunjuk masa depan.
Jangan menuliskan proses pemeriksaan tersebut ke output.
"""


def dump(path, value, exclusive=False):
    with path.open("x" if exclusive else "w", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)


def select_jobs(jobs, size):
    """Diagnostic coverage sample, not a statistically representative cost sample."""
    buckets = defaultdict(list)
    for job in jobs:
        buckets[(job["case_name"], job["source"]["label_intent"])].append(job)
    for bucket in buckets.values():
        bucket.sort(key=lambda j: hashlib.sha256(j["job_id"].encode()).hexdigest())
    selected, used = [], set()
    label_counts = Counter()
    def take(key):
        bucket = buckets[key]
        while bucket and bucket[0]["job_id"] in used:
            bucket.pop(0)
        if bucket:
            job = bucket.pop(0)
            selected.append(job)
            used.add(job["job_id"])
            label_counts[key[1]] += 1
    # Cover every case first; then cover additional case/intent combinations.
    for case in base.CASES:
        keys = [k for k in buckets if k[0] == case and buckets[k]]
        if keys and len(selected) < size:
            take(min(keys, key=lambda k: (label_counts[k[1]], k[1])))
    covered = {(j["case_name"], j["source"]["label_intent"]) for j in selected}
    for key in sorted(buckets, key=lambda k: (k in covered, k[1], k[0])):
        if len(selected) < size and key not in covered:
            take(key)
    while len(selected) < size:
        before = len(selected)
        for key in sorted(buckets):
            if len(selected) < size:
                take(key)
        if len(selected) == before:
            break
    if len(selected) != size:
        raise ValueError("Not enough unfinished jobs for this trial.")
    return selected


def remaining_jobs(jobs, completed_dir):
    if completed_dir is None:
        return jobs
    remaining = []
    for job in jobs:
        path = completed_dir / (job["job_id"] + ".json")
        if not path.exists():
            remaining.append(job)
            continue
        item = json.loads(path.read_text(encoding="utf-8"))
        # Checkpoint dari jadwal kasus lama atau yang gagal aturan terbaru dianggap belum selesai.
        try:
            if item.get("job") != job:
                raise ValueError("Checkpoint job changed.")
            base.validate_session(item["session"], job)
        except (ValueError, KeyError):
            remaining.append(job)
    return remaining


def make_request(jobs, max_tokens, model=MODEL_ID, temperature=0.3, effort=None):
    inference, extra = base.bedrock_request_options(model, max_tokens, temperature, effort)
    return {
        "system": [{"text": PROMPT}],
        "messages": [{"role": "user", "content": [{"text": json.dumps({"jobs": [base.job_for_model(job) for job in jobs]}, ensure_ascii=False, separators=(",", ":"))}]}],
        "inferenceConfig": inference,
        **({"additionalModelRequestFields": extra} if extra else {}),
        "outputConfig": {"textFormat": {"type": "json_schema", "structure": {
            "jsonSchema": {"name": "hostage_dataset", "schema": json.dumps(Batch.model_json_schema())}
        }}},
    }


def cost_from_usage(usage, price_input=PRICE_INPUT, price_output=PRICE_OUTPUT):
    # No cache checkpoints or thinking are requested. Refuse to invent unknown usage.
    for key in ("inputTokens", "outputTokens"):
        if type(usage.get(key)) is not int or usage[key] < 0:
            return {"usd_before_tax": None, "reason": "Missing/invalid token usage", "usage": usage}
    if usage.get("cacheReadInputTokens", 0) or usage.get("cacheWriteInputTokens", 0):
        return {"usd_before_tax": None, "reason": "Unexpected cache usage; requires cache pricing", "usage": usage}
    if price_input is None or price_output is None:
        return {"usd_before_tax": None, "reason": "Model price not provided", "usage": usage}
    total = (Decimal(usage["inputTokens"]) * price_input + Decimal(usage["outputTokens"]) * price_output) / Decimal(1000000)
    return {"usd_before_tax": str(total), "usage": usage, "price_per_million": {"input": str(price_input), "output": str(price_output)}, "price_source": PRICE_SOURCE,
            "basis": "Public Global Standard token rates; excludes tax/discounts; AWS bill is authoritative."}


def validate_results(payload, jobs, generation_settings=None):
    if not isinstance(payload, dict) or set(payload) != {"results"} or not isinstance(payload["results"], list):
        raise ValueError("Response must contain only a results array.")
    expected = {j["job_id"]: j for j in jobs}
    ids = [item.get("job_id") if isinstance(item, dict) else None for item in payload["results"]]
    if any(not isinstance(i, str) for i in ids) or len(ids) != len(set(ids)) or set(ids) - set(expected):
        raise ValueError("Duplicate, malformed, or unknown job IDs; batch quarantined.")
    accepted, rejected = [], []
    for raw in payload["results"]:
        job = expected[raw["job_id"]]
        try:
            item = Item.model_validate(raw).model_dump()
            session = base.validate_session(item["session"], job)
            if session["focus_player"] and session["focus_player"] not in session["participants"]:
                raise ValueError("focus_player must be a participant or empty.")
            if any(p.casefold() in {"aku", "saya", "gue", "gua", "gw", "lu", "lo", "anda"} for p in session["participants"]):
                raise ValueError("Pronouns are not player names.")
            accepted.append({"job": job, "session": session, "model_verification_passed": False,
                             "validation_status": "local_structure_only", "human_review_status": "pending",
                             "generation_settings": generation_settings or {"provider": "aws_bedrock", "model": MODEL_ID, "thinking": "disabled"}})
        except (ValueError, KeyError, TypeError, ValidationError) as exc:
            rejected.append({"job_id": job["job_id"], "reason": str(exc)})
    rejected.extend({"job_id": i, "reason": "Missing result"} for i in sorted(set(expected) - set(ids)))
    return accepted, rejected


def prepare_sender(region, profile=None, model=MODEL_ID):
    token = (os.getenv("AWS_BEARER_TOKEN_BEDROCK") or os.getenv("AMAZON_API_KEY") or "").strip()
    if token:
        import requests
        session = requests.Session()  # requests has no automatic retries by default.
        url = "https://bedrock-runtime." + region + ".amazonaws.com/model/" + quote(model, safe="") + "/converse-stream"
        progress = {"next": 0}
        def report(characters):
            # Tanda hidup di log setiap sekitar 5.000 karakter.
            if characters >= progress["next"]:
                print(f"stream: {characters:,} karakter diterima", flush=True)
                progress["next"] = characters + 5000
        return lambda body: base.converse_stream(session.post, url, token, body, on_text=report)
    try:
        import boto3
        from botocore.config import Config
    except ImportError:
        raise RuntimeError("AWS credentials unavailable: set AWS_BEARER_TOKEN_BEDROCK in local .env, or install boto3 and configure an AWS profile.") from None
    session = boto3.Session(profile_name=profile, region_name=region)
    if session.get_credentials() is None:
        raise RuntimeError("No AWS credentials found. Configure a Bedrock API key or AWS profile.")
    client = session.client("bedrock-runtime", config=Config(connect_timeout=20, read_timeout=1800, retries={"total_max_attempts": 1}))
    return lambda body: client.converse(modelId=model, **body)


def run_once(directory, request, jobs, sender, *, usage_cost_fn=cost_from_usage, generation_settings=None):
    # Atomic marker prevents accidentally paying twice when a response is lost.
    dump(directory / "attempt.json", {"started_utc": datetime.now(timezone.utc).isoformat(), "max_requests": 1}, exclusive=True)
    try:
        response = sender(request)
    except Exception as exc:
        dump(directory / "failure.json", {"error_type": type(exc).__name__, "status": "request_failed_or_response_unknown", "automatic_retry": False, "http_status": getattr(exc, "http_status", None), "aws_error_type": getattr(exc, "aws_error_type", None), "provider_message": getattr(exc, "provider_message", None)})
        raise RuntimeError("Bedrock request failed (" + type(exc).__name__ + "). No retry. Inspect AWS request/billing status before making another attempt.") from None
    dump(directory / "response.json", response)
    cost = usage_cost_fn(response.get("usage", {}))
    dump(directory / "usage_cost.json", cost)
    if response.get("stopReason") != "end_turn":
        dump(directory / "validation.json", {"accepted": 0, "status": "incomplete_or_blocked", "stop_reason": response.get("stopReason")})
        raise RuntimeError("Response incomplete/blocked; retained raw response and token usage. No retry.")
    try:
        content = response["output"]["message"]["content"]
        text = "".join(block.get("text", "") for block in content)
        accepted, rejected = validate_results(json.loads(text), jobs, generation_settings)
    except (KeyError, TypeError, ValueError) as exc:
        dump(directory / "validation.json", {"accepted": 0, "status": "invalid_batch", "reason": str(exc)})
        raise RuntimeError("Invalid batch; raw response and token usage retained. No retry.") from None
    for item in accepted:
        dump(directory / (item["job"]["job_id"] + ".json"), item, exclusive=True)
    if accepted:
        base.export_records(accepted, directory / "draft.csv", directory / "draft.groups.jsonl")
        # Keep review status explicit in companion metadata too.
        group_path = directory / "draft.groups.jsonl"
        groups = [json.loads(line) for line in group_path.read_text(encoding="utf-8").splitlines()]
        for group in groups:
            group.update(model_verification_passed=False, validation_status="local_structure_only", human_review_status="pending")
        group_path.write_text("".join(json.dumps(g, ensure_ascii=False) + "\n" for g in groups), encoding="utf-8")
    summary = {"requested": len(jobs), "accepted_local_structure": len(accepted), "rejected": rejected,
               "model_verification": "not_run", "human_review": "pending", "generation_requests": 1,
               "cost": cost, "sample_purpose": "case coverage; not representative of production cost"}
    dump(directory / "validation.json", summary)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=base.PROJECT_ROOT / "ai_2_dataset_baru/data/dataset_final3.csv")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--completed-dir", type=Path)
    parser.add_argument("--batch-size", type=int, default=50)
    parser.add_argument("--max-output-tokens", type=int, default=64000)
    parser.add_argument("--region", default="us-east-1")
    parser.add_argument("--profile")
    parser.add_argument("--env-file", type=Path, default=base.PROJECT_ROOT / ".env")
    parser.add_argument("--model", default=MODEL_ID, help="ID model/inference profile Bedrock")
    parser.add_argument("--effort", choices=["low", "medium", "high", "xhigh", "max"], help="Kedalaman berpikir Claude generasi baru")
    parser.add_argument("--price-input", type=Decimal, help="USD per 1 juta token input; default hanya untuk Haiku")
    parser.add_argument("--price-output", type=Decimal, help="USD per 1 juta token output; default hanya untuk Haiku")
    parser.add_argument("--generate", action="store_true")
    args = parser.parse_args()
    if args.model == MODEL_ID and args.price_input is None and args.price_output is None:
        args.price_input, args.price_output = PRICE_INPUT, PRICE_OUTPUT
    if not 1 <= args.batch_size <= 50 or not 1 <= args.max_output_tokens <= 64000:
        parser.error("Trial permits 1-50 examples and 1-64000 output tokens.")
    if not re.fullmatch(r"[a-z]{2}-[a-z]+-\d", args.region):
        parser.error("Invalid commercial AWS region.")
    load_dotenv(args.env_file)
    jobs = base.plan_jobs(base.read_source(args.input), 1)
    remaining = remaining_jobs(jobs, args.completed_dir)
    selected = select_jobs(remaining, args.batch_size)
    request = make_request(selected, args.max_output_tokens, args.model, effort=args.effort)
    manifest = {"model": args.model, "region": args.region, "source_sha256": hashlib.sha256(args.input.read_bytes()).hexdigest(),
                "base_script_sha256": hashlib.sha256(Path(base.__file__).read_bytes()).hexdigest(),
                "trial_script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                "request_sha256": hashlib.sha256(json.dumps(request, sort_keys=True, ensure_ascii=False).encode()).hexdigest(),
                "planned_total": len(jobs), "unfinished_total": len(remaining), "selected": len(selected),
                "case_counts": dict(Counter(j["case_name"] for j in selected)),
                "intent_counts": dict(Counter(j["source"]["label_intent"] for j in selected)),
                "total_messages": sum(j["jumlah_pesan"] for j in selected),
                "verification": "local_structure_only", "automatic_retries": 0,
                "max_output_tokens": args.max_output_tokens, "sample_purpose": "diagnostic case coverage"}
    directory = args.output_dir.resolve()
    directory.mkdir(parents=True, exist_ok=True)
    manifest_path = directory / "plan.json"
    if (directory / "attempt.json").exists():
        parser.error("This trial was already attempted. No second request is allowed in this output directory.")
    if manifest_path.exists() and json.loads(manifest_path.read_text(encoding="utf-8")) != manifest:
        parser.error("Plan changed; use a new output directory.")
    dump(manifest_path, manifest)
    dump(directory / "request.json", request)
    dump(directory / "jobs.json", selected)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    if not args.generate:
        print("DRY RUN: no API calls. Request is ready for review.")
        return
    try:
        sender = prepare_sender(args.region, args.profile, args.model)
    except Exception as exc:
        dump(directory / "preflight.json", {"status": "blocked_credentials_or_sdk", "error_type": type(exc).__name__, "generation_requests": 0})
        print("BLOCKED: AWS credentials/SDK are not available. Add AWS_BEARER_TOKEN_BEDROCK to local .env, or configure an AWS profile with boto3. No generation request sent.", file=sys.stderr)
        raise SystemExit(2)
    summary = run_once(directory, request, selected, sender,
                       usage_cost_fn=lambda usage: cost_from_usage(usage, args.price_input, args.price_output),
                       generation_settings={"provider": "aws_bedrock", "model": args.model, "thinking": "not_requested"})
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
