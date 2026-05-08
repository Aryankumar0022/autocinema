import httpx, os
from dotenv import load_dotenv
load_dotenv()
key = os.getenv("HF_API_KEY")
r = httpx.post(
    "https://api-inference.huggingface.co/models/facebook/musicgen-small",
    json={"inputs": "cinematic ambient"},
    headers={"Authorization": f"Bearer {key}"},
    timeout=60,
)
print(r.status_code, len(r.content), r.headers.get("content-type", ""))
if r.status_code != 200:
    print(r.text[:300])
