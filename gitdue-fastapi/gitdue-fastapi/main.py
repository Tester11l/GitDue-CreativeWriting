"""GitDue website: FastAPI + Jinja2. Jalankan: python main.py  (atau: uvicorn main:app)"""
import json, os, re, smtplib, ssl, time, urllib.request, urllib.error
from datetime import datetime
from email.message import EmailMessage
from pathlib import Path
from urllib.parse import urlparse

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

BASE = Path(__file__).parent

# Baca file .env sederhana (tanpa library tambahan). Di hosting, pakai Environment Variables.
env_file = BASE / ".env"
if env_file.exists():
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

TO_EMAIL = os.getenv("TO_EMAIL", "s32240166@student.ubm.ac.id")
BREVO_API_KEY = os.getenv("BREVO_API_KEY", "")
BREVO_SENDER = os.getenv("BREVO_SENDER", "")      # email pengirim yang sudah diverifikasi di Brevo
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")

FAQS = [
    ("Saya pemula total, apakah bisa ikut?", "Bisa. Kamu mulai dari tes penentuan level, lalu mendapat kelas yang pas. Bingung dan error itu bagian dari belajar."),
    ("Apa yang saya dapat di trial 7 hari?", "Akses ke kelas, tutor, dan fitur tes selama satu minggu tanpa biaya."),
    ("Bagaimana cara memilih tutor?", "Buka profil tutor untuk melihat spesialisasi, pengalaman, gaya mengajar, dan rating dari pengguna lain, lalu pilih yang paling cocok."),
    ("Perlu install software di laptop?", "Tidak. Coding playground berjalan di browser, di laptop maupun HP."),
    ("Apakah ada sertifikat?", "Ada. Sertifikat diberikan setelah kamu lulus ujian akhir kelas."),
    ("Bahasa apa saja yang diajarkan?", "Python, C++, C#, Java, JavaScript, React, dan SQL."),
]
PAKET = {"Tanya-tanya dulu", "Trial gratis 7 hari", "Paket bulanan", "Paket tahunan"}

app = FastAPI(title="GitDue", docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")
templates = Jinja2Templates(directory=BASE / "templates")
last_sent: dict[str, float] = {}


@app.middleware("http")
async def security_headers(request: Request, call_next):
    resp = await call_next(request)
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["X-Frame-Options"] = "SAMEORIGIN"
    resp.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return resp


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={"faqs": FAQS})


@app.get("/health")
def health():
    return {"status": "ok"}


class Contact(BaseModel):
    nama: str = ""
    email: str = ""
    paket: str = ""
    pesan: str = ""
    website: str = ""  # honeypot: harus kosong


def one_line(s: str) -> str:
    return re.sub(r"[\r\n\t]+", " ", s).strip()


def send_email(nama: str, email: str, paket: str, pesan: str) -> None:
    subject = f"[GitDue] Pesan baru dari {nama}"
    body = f"Nama  : {nama}\nEmail : {email}\nMinat : {paket}\nWaktu : {datetime.now():%d %b %Y %H:%M}\n\nPesan:\n{pesan}\n"
    if BREVO_API_KEY and BREVO_SENDER:  # lewat HTTPS, aman untuk hosting gratis yang blokir SMTP
        payload = json.dumps({
            "sender": {"name": "GitDue Website", "email": BREVO_SENDER},
            "to": [{"email": TO_EMAIL}],
            "replyTo": {"email": email, "name": nama},
            "subject": subject, "textContent": body,
        }).encode()
        req = urllib.request.Request("https://api.brevo.com/v3/smtp/email", data=payload, method="POST",
                                     headers={"api-key": BREVO_API_KEY, "content-type": "application/json", "accept": "application/json"})
        urllib.request.urlopen(req, timeout=15).read()
    elif SMTP_USER and SMTP_PASS:  # cocok untuk dijalankan di laptop / VPS
        msg = EmailMessage()
        msg["Subject"], msg["From"], msg["To"], msg["Reply-To"] = subject, SMTP_USER, TO_EMAIL, email
        msg.set_content(body)
        ctx = ssl.create_default_context()
        if SMTP_PORT == 465:
            with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=ctx, timeout=15) as s:
                s.login(SMTP_USER, SMTP_PASS); s.send_message(msg)
        else:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15) as s:
                s.starttls(context=ctx); s.login(SMTP_USER, SMTP_PASS); s.send_message(msg)
    else:
        raise RuntimeError("Email belum dikonfigurasi (isi BREVO_API_KEY + BREVO_SENDER, atau SMTP_USER + SMTP_PASS).")


def reply(ok: bool, message: str, code: int = 200) -> JSONResponse:
    return JSONResponse({"ok": ok, "message": message}, status_code=code)


@app.post("/api/contact")
def contact(data: Contact, request: Request):
    origin = request.headers.get("origin")
    if origin and urlparse(origin).netloc != request.headers.get("host"):
        return reply(False, "Permintaan ditolak.", 403)
    if data.website:  # bot
        return reply(True, "Terima kasih! Pesanmu sudah terkirim.")
    ip = (request.headers.get("x-forwarded-for") or (request.client.host if request.client else "?")).split(",")[0].strip()
    if time.time() - last_sent.get(ip, 0) < 30:
        return reply(False, "Tunggu sebentar sebelum mengirim pesan lagi.", 429)

    nama, email, pesan = one_line(data.nama), one_line(data.email), data.pesan.strip()
    paket = one_line(data.paket) if one_line(data.paket) in PAKET else "Tanya-tanya dulu"
    if not nama or len(nama) > 80:
        return reply(False, "Isi nama kamu (maksimal 80 karakter).", 422)
    if len(email) > 120 or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        return reply(False, "Alamat email belum valid.", 422)
    if not pesan or len(pesan) > 2000:
        return reply(False, "Isi pesan (maksimal 2000 karakter).", 422)
    last_sent[ip] = time.time()

    # Cadangan: simpan ke file (di hosting gratis, disk bisa hilang saat redeploy).
    try:
        (BASE / "data").mkdir(exist_ok=True)
        with open(BASE / "data" / "messages.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps({"time": datetime.now().isoformat(), "nama": nama, "email": email, "paket": paket, "pesan": pesan}, ensure_ascii=False) + "\n")
    except OSError:
        pass

    try:
        send_email(nama, email, paket, pesan)
    except Exception as e:  # noqa: BLE001
        print("EMAIL ERROR:", repr(e))
        return reply(False, f"Maaf, email belum berhasil terkirim. Coba lagi nanti atau hubungi {TO_EMAIL}.", 503)
    return reply(True, "Terima kasih! Pesanmu sudah terkirim. Kami akan membalas lewat email.")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
