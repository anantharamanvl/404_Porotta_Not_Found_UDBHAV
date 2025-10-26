# detector.py
import re
from urllib.parse import urlparse

SUSPICIOUS_KEYWORDS = [
    "verify", "suspend", "password reset", "account suspension", "update delivery",
    "click here", "confirm", "immediate", "unauthorized", "failed", "action required"
]
SUSPICIOUS_DOMAINS = ["malicious.click", "phish-serve.ru"]

def check_link(url):
    """Return True if link appears suspicious."""
    try:
        parsed = urlparse(url)
        hostname = parsed.hostname or ""
        # IP address like 192.168.0.77
        is_ip = re.match(r"^\d+\.\d+\.\d+\.\d+$", hostname) is not None
        bad_domain = any(bad in hostname for bad in SUSPICIOUS_DOMAINS)
        odd_protocol = parsed.scheme not in ("http", "https")
        return is_ip or bad_domain or odd_protocol
    except Exception:
        return True

def check_sender(from_addr):
    """Return True if sender domain looks suspicious."""
    m = re.search(r"@([A-Za-z0-9\.\-]+)", from_addr)
    if m:
        domain = m.group(1)
        # sender as IP or known bad domain is suspicious
        if re.match(r"^\d+\.\d+\.\d+\.\d+$", domain):
            return True
        if any(bad in domain for bad in SUSPICIOUS_DOMAINS):
            return True
    return False

def keyword_score(text):
    """Simple count of suspicious keywords in text."""
    text_l = text.lower()
    score = 0
    for kw in SUSPICIOUS_KEYWORDS:
        if kw in text_l:
            score += 1
    return score

def detect(email):
    """
    Input: email dict with keys 'from','subject','body','link'
    Output: dict with verdict, score, reasons
    """
    reasons = []
    score = 0

    link = email.get("link","")
    if link and check_link(link):
        score += 3
        reasons.append("Suspicious link")

    if check_sender(email.get("from","")):
        score += 2
        reasons.append("Suspicious sender domain")

    k = keyword_score(email.get("subject","") + " " + email.get("body",""))
    if k > 0:
        score += k
        reasons.append(f"Suspicious keywords ({k})")

    verdict = "phishing" if score >= 3 else "benign"
    return {"verdict": verdict, "score": score, "reasons": reasons}
