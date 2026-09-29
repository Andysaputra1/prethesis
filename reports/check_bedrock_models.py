"""Read-only Bedrock model availability; no inference."""
import json, os
from pathlib import Path
from urllib.parse import quote
import requests
from dotenv import load_dotenv
root=Path(__file__).resolve().parents[1]
load_dotenv(root/'.env')
token=(os.getenv('AWS_BEARER_TOKEN_BEDROCK') or os.getenv('AMAZON_API_KEY') or '').strip()
results=[]
for model in ['openai.gpt-6-sol','anthropic.claude-sonnet-5','anthropic.claude-haiku-4-5-20251001-v1:0']:
    r=requests.get('https://bedrock.us-east-1.amazonaws.com/foundation-model-availability/'+quote(model,safe=''),headers={'Authorization':'Bearer '+token},timeout=30,allow_redirects=False)
    try: body=r.json()
    except ValueError: body={}
    entry={'model':model,'http_status':r.status_code,'availability':body if r.status_code==200 else {'message':str(body.get('message','')).replace(token,'[REDACTED]')[:800]}}
    results.append(entry)
(root/'reports/bedrock_model_availability.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
print(json.dumps(results,indent=2))
