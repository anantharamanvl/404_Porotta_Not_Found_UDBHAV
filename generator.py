# generator.py
import json
import random

# load templates from a small built-in list (no external file needed)
TEMPLATES = [
    {
        "id": "bank_wrong_link",
        "subject": "Important: Verify your account immediately",
        "body": "Dear {name},\n\nWe detected suspicious activity on your account. Please verify your identity by clicking the link below to avoid account suspension:\n\n{link}\n\nThanks,\n{org} Security Team",
        "placeholders": {"org": "Acme Bank"}
    },
    {
        "id": "package_delivery",
        "subject": "Your package delivery failed — action required",
        "body": "Hello {name},\n\nYour package delivery could not be completed. Please update delivery details: {link}\n\nRegards,\n{org}",
        "placeholders": {"org": "ShipFast"}
    },
    {
        "id": "it_password_reset",
        "subject": "Company IT: Password reset required",
        "body": "Hi {name},\n\nWe require an immediate password reset due to security reasons. Reset here: {link}\n\nIT Support",
        "placeholders": {"org": "YourCompany IT"}
    }
]

NAMES = ["Ananthan", "Priya", "Amit", "Sara", "Rohit"]
SAFE_DOMAINS = ["example.com", "yourcompany.com", "acme.com"]
SUSPICIOUS_HOSTS = ["192.168.0.77", "malicious.click", "phish-serve.ru"]

def make_link(safe=True):
    """Return a safe-looking or suspicious link."""
    if safe:
        domain = random.choice(SAFE_DOMAINS)
        return f"https://{domain}/verify?uid={random.randint(1000,9999)}"
    else:
        host = random.choice(SUSPICIOUS_HOSTS)
        return f"http://{host}/login.php?ref={random.randint(100,999)}"

def generate_email(template_id=None, phishing=True):
    """Return a dict that represents an email."""
    tpl = None
    if template_id:
        for t in TEMPLATES:
            if t["id"] == template_id:
                tpl = t
                break
    if not tpl:
        tpl = random.choice(TEMPLATES)

    name = random.choice(NAMES)
    org = tpl.get("placeholders", {}).get("org", "Support")
    link = make_link(safe=not phishing)

    # Construct a From address: phishing may use suspicious host
    if phishing:
        from_addr = f"support@{random.choice(SUSPICIOUS_HOSTS)}"
    else:
        from_addr = f"no-reply@{random.choice(SAFE_DOMAINS)}"

    subject = tpl["subject"]
    body = tpl["body"].format(name=name, link=link, org=org)

    return {
        "from": from_addr,
        "subject": subject,
        "body": body,
        "link": link,
        "is_phishing_intent": phishing
    }

# quick demo when running generator directly
if __name__ == "__main__":
    print(generate_email(phishing=True))
