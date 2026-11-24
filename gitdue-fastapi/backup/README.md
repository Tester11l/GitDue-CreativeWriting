# GitDue Website (FastAPI + uvicorn)

Isi folder:
- main.py            : server (halaman + endpoint form kontak)
- templates/index.html, static/ : tampilan
- requirements.txt   : daftar library (fastapi, uvicorn, jinja2)
- .env.example       : contoh pengaturan email (salin jadi .env)
- run.bat / run.sh   : jalankan dengan sekali klik
- render.yaml, Procfile : untuk deploy online

Tidak perlu venv, tidak perlu database. Butuh Python 3.9 atau lebih baru.

## 1. Jalankan di laptop (tanpa venv)

Windows: klik dua kali `run.bat`
Mac / Linux: `sh run.sh`

Atau manual di terminal (dalam folder ini):

    pip install -r requirements.txt
    uvicorn main:app --reload

Buka http://localhost:8000
(Kalau pakai run.bat / run.sh / `python main.py`, alamatnya juga http://localhost:8000.)

Kalau muncul error "externally-managed-environment" (Linux/Mac), tambahkan
`--break-system-packages` di belakang perintah pip.

## 2. Setup email form kontak (wajib supaya pesan masuk)

Pesan dikirim ke s32240166@student.ubm.ac.id (ubah lewat TO_EMAIL).
Salin `.env.example` jadi `.env`, lalu pilih salah satu cara:

### Cara A: Brevo (disarankan, jalan di hosting gratis)
Hosting gratis seperti Render memblokir SMTP, jadi email dikirim lewat HTTPS API.
1. Daftar gratis di brevo.com.
2. Di menu Senders, domains & dedicated IPs, tambahkan Sender (pakai email kamu, misalnya
   Gmail atau email kampus) lalu verifikasi lewat email yang dikirim Brevo.
3. Di menu SMTP & API, buat API Key (tab API Keys).
4. Isi di .env:
       BREVO_API_KEY=isi_api_key
       BREVO_SENDER=email_sender_yang_sudah_diverifikasi
5. Restart server, kirim pesan percobaan dari form, cek inbox dan spam.
(Nama menu di Brevo bisa berubah. Kalau beda, cari menu Senders dan API Keys.)

### Cara B: SMTP Gmail (hanya untuk laptop atau VPS)
1. Pakai akun Gmail, aktifkan verifikasi 2 langkah, buat App Password.
2. Isi SMTP_USER (alamat Gmail) dan SMTP_PASS (App Password 16 karakter) di .env.

Kalau email belum diatur, form akan menampilkan pesan gagal. Setiap pesan yang lolos
validasi juga dicatat di data/messages.jsonl (di hosting gratis, file ini bisa hilang
saat redeploy).

## 3. Deploy online gratis di Render

Render menyediakan web service gratis untuk FastAPI.

1. Buat akun GitHub, lalu upload folder ini sebagai repository baru.
   PENTING: jangan upload file .env (sudah ada di .gitignore).
2. Daftar di render.com (bisa login pakai GitHub).
3. Klik New, pilih Web Service, lalu pilih repository tadi.
4. Isi pengaturan:
   - Language / Runtime: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Instance Type: Free
5. Di bagian Environment Variables tambahkan:
   - TO_EMAIL = s32240166@student.ubm.ac.id
   - BREVO_API_KEY = (API key dari Brevo)
   - BREVO_SENDER = (email sender yang sudah diverifikasi)
6. Klik Create Web Service dan tunggu build selesai. Websitemu hidup di
   https://nama-servicemu.onrender.com
   (Cara cepat: pilih New, Blueprint, lalu Render membaca render.yaml.)

Hal yang perlu kamu tahu tentang paket gratis Render:
- Service tidur setelah sekitar 15 menit tidak ada pengunjung. Kunjungan pertama setelah
  itu bisa lambat 30 sampai 60 detik. Normal, bukan error. Untuk presentasi, buka website
  beberapa menit sebelumnya supaya sudah bangun.
- SMTP diblokir di paket gratis, makanya dipakai Brevo (Cara A).
- Disk tidak permanen, jadi data/messages.jsonl bisa hilang. Email jadi catatan utama.
- Domain sendiri (misalnya gitdue.id) umumnya butuh paket berbayar. Cek halaman Render
  untuk aturan terbaru.

Platform gratis lain (Koyeb, Fly.io, Railway, dll) juga bisa menjalankan uvicorn dengan
Start Command yang sama, tapi kuota dan syarat gratisnya sering berubah. Cek situsnya
dulu sebelum memilih.

## 4. Mengubah isi website
- Teks dan layout: templates/index.html
- Warna dan gaya: static/style.css (warna ada di bagian :root paling atas)
- Pertanyaan FAQ: daftar FAQS di main.py
- Harga, nama tutor, dan rating di website masih contoh. Ganti sesuai keputusan kelompok.
