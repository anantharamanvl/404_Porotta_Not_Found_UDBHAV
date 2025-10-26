# app.py
from flask import Flask, render_template, request, redirect, url_for, jsonify, Response, send_file
from generator import generate_email
from detector import detect
import io, csv, json
import datetime

app = Flask(__name__)

# in-memory store for demo emails
EMAILS = []

def timestamp_now():
    return datetime.datetime.utcnow().isoformat() + "Z"

@app.route("/")
def index():
    emails = list(reversed(EMAILS[-200:]))
    return render_template("index.html", emails=emails)

@app.route("/generate", methods=["POST"])
def generate():
    phishing = request.form.get("phishing", "true").lower() == "true"
    email = generate_email(phishing=phishing)
    result = detect(email)
    email_record = {
        **email,
        **{
            "detected": result,
            "created_at": timestamp_now()
        }
    }
    EMAILS.append(email_record)
    return redirect(url_for("index"))

@app.route("/api/generate", methods=["POST"])
def api_generate():
    payload = request.get_json(silent=True) or {}
    phishing = payload.get("phishing", True)
    email = generate_email(phishing=phishing)
    result = detect(email)
    email_record = {
        **email,
        **{"detected": result, "created_at": timestamp_now()}
    }
    EMAILS.append(email_record)
    return jsonify(email_record)

@app.route("/api/emails", methods=["GET"])
def api_emails():
    return jsonify(list(reversed(EMAILS[-200:])))

# Download full report (CSV or JSON)
@app.route("/download_report")
def download_report():
    fmt = request.args.get("format", "csv").lower()
    emails = list(reversed(EMAILS[-200:]))

    if fmt == "json":
        data = json.dumps(emails, indent=2)
        return Response(
            data,
            mimetype="application/json",
            headers={"Content-Disposition": "attachment;filename=phishguard_report.json"},
        )

    # default CSV
    si = io.StringIO()
    writer = csv.writer(si)
    writer.writerow(["created_at","from","subject","body","link","detected_verdict","detected_score","detected_reasons"])
    for e in emails:
        detected = e.get("detected", {})
        body = e.get("body","").replace("\n", "\\n")
        reasons = "; ".join(detected.get("reasons", []))
        writer.writerow([
            e.get("created_at",""),
            e.get("from",""),
            e.get("subject",""),
            body,
            e.get("link",""),
            detected.get("verdict",""),
            detected.get("score",""),
            reasons
        ])
    output = si.getvalue()
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=phishguard_report.csv"},
    )

# Download a single email in simple .eml-like text format
@app.route("/download_email/<int:index>")
def download_email(index):
    # index is the index in the reversed list shown on UI (0 is newest)
    emails = list(reversed(EMAILS[-200:]))
    if index < 0 or index >= len(emails):
        return ("Not found", 404)
    e = emails[index]
    # Build a basic .eml text
    eml = []
    eml.append(f"From: {e.get('from','')}")
    eml.append(f"Subject: {e.get('subject','')}")
    eml.append(f"Date: {e.get('created_at','')}")
    eml.append("")
    eml.append(e.get("body",""))
    eml_text = "\n".join(eml)
    return Response(
        eml_text,
        mimetype="message/rfc822",
        headers={"Content-Disposition": f"attachment;filename=email_{index}.eml"},
    )
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
