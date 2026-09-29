"""Read-only Anthropic prerequisite check; no inference and no form submission."""
import json
import os
from pathlib import Path
import requests
from dotenv import load_dotenv

root = Path(__file__).resolve().parents[1]
load_dotenv(root / ".env")
token = (os.getenv("AWS_BEARER_TOKEN_BEDROCK") or os.getenv("AMAZON_API_KEY") or "").strip()
if not token:
    raise SystemExit("No Bedrock API key configured.")
try:
    response = requests.get("https://bedrock.us-east-1.amazonaws.com/use-case-for-model-access", headers={"Authorization": "Bearer " + token}, timeout=(20, 30), allow_redirects=False)
    try:
        body = response.json()
    except ValueError:
        body = {}
    result = {"operation": "GetUseCaseForModelAccess", "http_status": response.status_code, "has_submitted_form": bool(body.get("formData")) if response.status_code == 200 else None, "generation_requests": 0}
    if response.status_code != 200:
        result["provider_message"] = str(body.get("message", "")).replace(token, "[REDACTED]")[:1000]
except requests.RequestException as exc:
    result = {"operation": "GetUseCaseForModelAccess", "error_type": type(exc).__name__, "generation_requests": 0}
(root / "reports/bedrock_access_status.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps(result, indent=2))
