from fastapi import APIRouter
from pydantic import BaseModel
import re

router = APIRouter(prefix="/threat", tags=["threat"])

MALICIOUS_DOMAINS = {"evil-site.com", "phishing-bank.net", "malware-dl.xyz", "fake-login.com", "virus-update.org"}
SUSPICIOUS_PATTERNS = [r"login.*verify.*now", r"urgent.*account.*suspend", r"free.*gift.*click", r"crypto.*double.*return"]

class URLCheckRequest(BaseModel):
    url: str

class URLCheckResponse(BaseModel):
    url: str
    safe: bool
    score: int
    reasons: list[str]

def extract_domain(url: str) -> str:
    url = url.lower().strip()
    url = re.sub(r"^https?://", "", url)
    url = re.sub(r"^www\\.", "", url)
    return url.split("/")[0]

@router.post("/check-url", response_model=URLCheckResponse)
async def check_url(req: URLCheckRequest):
    domain = extract_domain(req.url)
    reasons = []
    score = 0
    if domain in MALICIOUS_DOMAINS:
        score = 100
        reasons.append("Known malicious domain")
    if "https" not in req.url.lower():
        score += 20
        reasons.append("No HTTPS")
    if any(re.search(p, req.url, re.I) for p in SUSPICIOUS_PATTERNS):
        score += 30
        reasons.append("Phishing pattern detected")
    if len(req.url) > 200:
        score += 10
        reasons.append("URL obfuscation")
    if re.match(r"https?://\\d+\\.\\d+\\.\\d+\\.\\d+", req.url):
        score += 25
        reasons.append("IP-based URL")
    score = min(score, 100)
    return URLCheckResponse(url=req.url, safe=score < 50, score=score, reasons=reasons if reasons else ["No threats detected"])
