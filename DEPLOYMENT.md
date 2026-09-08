# Deployment Guide

Arsitektur deployment split:
- **Frontend (Vue 3)** → Vercel (static hosting)
- **Backend (Django)** → Railway (persistent container)
- **Database** → Railway MySQL plugin
- **Media Storage** → (opsional) Cloudflare R2 / AWS S3

---

## Prasyarat

- Akun [Railway](https://railway.app)
- Akun [Vercel](https://vercel.com)
- Repo sudah di-push ke GitHub

---

## 1. Deploy Backend ke Railway

### 1.1 Buat Project

1. Login ke [railway.app](https://railway.app)
2. **New Project** → **Deploy from GitHub repo**
3. Pilih repo `face_recognition`
4. Railway otomatis membaca `railway.toml` dan `Procfile`

### 1.2 Tambah MySQL Database

1. Di project Railway → **+ New Service** → **Database** → **MySQL**
2. Railway otomatis inject environment variables berikut ke semua service dalam project:
   ```
   MYSQL_HOST
   MYSQL_USER
   MYSQL_PASSWORD
   MYSQL_DATABASE
   MYSQL_PORT
   ```
   Tidak perlu diisi manual — sudah tersambung otomatis.

### 1.3 Set Environment Variables Backend

Di service Django → tab **Variables**, tambahkan:

| Variable | Nilai | Keterangan |
|---|---|---|
| `SECRET_KEY` | string random panjang | Wajib. Generate di [djecrety.ir](https://djecrety.ir) |
| `DEBUG` | `False` | Wajib production |
| `FRONTEND_URL` | `https://nama-app.vercel.app` | Diisi setelah Vercel deploy |
| `RAILWAY_PUBLIC_DOMAIN` | (otomatis) | Di-inject Railway, untuk ALLOWED_HOSTS |

> **Catatan:** `MYSQL_*` variables sudah otomatis tersedia dari MySQL plugin, tidak perlu diisi ulang.

### 1.4 Jalankan Migrasi

Railway menjalankan `python manage.py migrate --noinput` otomatis via `railway.toml` buildCommand. Jika perlu manual:

```bash
# Di Railway dashboard → service → Shell tab
python manage.py migrate
python manage.py createsuperuser
```

### 1.5 Catat URL Backend

Setelah deploy selesai, Railway memberikan URL seperti:
```
https://face-recognition-production.up.railway.app
```
URL ini dibutuhkan untuk setup Vercel dan environment variable `FRONTEND_URL`.

---

## 2. Deploy Frontend ke Vercel

### 2.1 Buat Project

1. Login ke [vercel.com](https://vercel.com)
2. **New Project** → **Import** repo `face_recognition`
3. **Root Directory**: ubah ke `frontend`
4. Framework otomatis terdeteksi sebagai **Vite**
5. Build Command: `npm run build` (sudah default)
6. Output Directory: `dist` (sudah default)

### 2.2 Set Environment Variables Frontend

Di Vercel → **Settings** → **Environment Variables**, tambahkan:

| Variable | Nilai | Keterangan |
|---|---|---|
| `VITE_BACKEND_URL` | `https://face-recognition-production.up.railway.app` | URL Railway dari langkah 1.5 |
| `VITE_SSO_TOKEN_URL` | (sudah di `.env.production`) | Opsional, override jika berbeda |

> **Penting:** Semua `VITE_*` variables harus diset di Vercel dashboard untuk production build. Nilai di `.env.production` hanya fallback.

### 2.3 Deploy

Klik **Deploy**. Vercel akan:
1. Install dependencies (`npm install`)
2. Build (`npm run build`) — menghasilkan `dist/`
3. Serve `dist/` sebagai static site
4. Semua route yang bukan file statis di-rewrite ke `index.html` (Vue Router history mode)

### 2.4 Update FRONTEND_URL di Railway

Setelah Vercel selesai dan URL frontend diketahui (misal `https://face-ai.vercel.app`), kembali ke Railway dan update:
```
FRONTEND_URL=https://face-ai.vercel.app
```
Ini dibutuhkan agar CORS backend hanya menerima request dari domain frontend.

---

## 3. Setup Media Storage (Wajib untuk Production)

> **Masalah:** Railway menggunakan ephemeral filesystem — semua file yang diupload (foto wajah, forensik, snapshot) **akan hilang** saat redeploy atau restart.

### Pilihan Storage

| Pilihan | Harga | Kemudahan |
|---|---|---|
| **Cloudflare R2** | Free 10GB/bulan | ⭐⭐⭐ |
| **AWS S3** | ~$0.023/GB | ⭐⭐ |
| **Backblaze B2** | Free 10GB | ⭐⭐⭐ |

### 3.1 Setup dengan django-storages + S3-compatible

Install tambahan (tambahkan ke `requirements.txt`):
```
django-storages[s3]==1.14.4
boto3==1.35.0
```

Tambahkan ke `core/settings.py`:
```python
# ─── MEDIA STORAGE (S3-compatible) ───────────────────────────────────────────
if os.environ.get('USE_S3') == 'True':
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_ENDPOINT_URL = os.environ.get('AWS_S3_ENDPOINT_URL')  # Untuk R2/B2
    AWS_S3_CUSTOM_DOMAIN = os.environ.get('AWS_S3_CUSTOM_DOMAIN')
    AWS_DEFAULT_ACL = 'public-read'
    AWS_S3_FILE_OVERWRITE = False
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/' if AWS_S3_CUSTOM_DOMAIN else f'{AWS_S3_ENDPOINT_URL}/{AWS_STORAGE_BUCKET_NAME}/'
```

Environment variables Railway yang perlu ditambahkan:
```
USE_S3=True
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_STORAGE_BUCKET_NAME=face-recognition-media
AWS_S3_ENDPOINT_URL=https://<account_id>.r2.cloudflarestorage.com  # untuk R2
AWS_S3_CUSTOM_DOMAIN=pub-xxxx.r2.dev  # public domain R2
```

### 3.2 Setup Cloudflare R2 (Rekomendasi)

1. Login ke [dash.cloudflare.com](https://dash.cloudflare.com) → **R2**
2. **Create bucket** → nama: `face-recognition-media`
3. **Settings** → aktifkan **Public access**
4. **Manage R2 API Tokens** → Create token dengan permission `Object Read & Write`
5. Catat:
   - Account ID (dari URL dashboard)
   - Access Key ID
   - Secret Access Key
   - Endpoint: `https://<account_id>.r2.cloudflarestorage.com`

---

## 4. Konfigurasi Lengkap Environment Variables

### Backend (Railway)

```env
# Django
SECRET_KEY=your-very-long-random-secret-key-here
DEBUG=False
FRONTEND_URL=https://your-app.vercel.app

# Database (otomatis dari MySQL plugin Railway)
MYSQL_DATABASE=railway
MYSQL_USER=root
MYSQL_PASSWORD=...
MYSQL_HOST=...
MYSQL_PORT=3306

# Media Storage (jika pakai S3/R2)
USE_S3=True
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_STORAGE_BUCKET_NAME=face-recognition-media
AWS_S3_ENDPOINT_URL=https://<account_id>.r2.cloudflarestorage.com
AWS_S3_CUSTOM_DOMAIN=pub-xxxx.r2.dev
```

### Frontend (Vercel)

```env
VITE_BACKEND_URL=https://your-app.up.railway.app
VITE_SSO_TOKEN_URL=https://sso.jogjaprov.go.id/realms/aptika/protocol/openid-connect/token
VITE_SSO_USERINFO_URL=https://sso.jogjaprov.go.id/realms/aptika/protocol/openid-connect/userinfo
VITE_SSO_CLIENT_ID=webopd
VITE_SSO_KEYCLOAK_BASE=https://sso.jogjaprov.go.id/realms/aptika/protocol/openid-connect
VITE_KEYCLOAK_URL=https://sso.jogjaprov.go.id
VITE_KEYCLOAK_CLIENT_ID=webopd
VITE_KEYCLOAK_REALM=aptika
VITE_API_URL=https://spl.jogjaprov.go.id/ai-cctv/
VITE_MAPBOX_ACCESS_TOKEN=pk.eyJ1...
```

---

## 5. Checklist Deployment

### Backend Railway
- [ ] Project dibuat dari GitHub repo
- [ ] MySQL plugin ditambahkan
- [ ] `SECRET_KEY` diset (bukan default insecure key)
- [ ] `DEBUG=False` diset
- [ ] Build berhasil (cek logs Railway)
- [ ] `python manage.py migrate` berjalan (via buildCommand)
- [ ] Superuser dibuat via Railway Shell
- [ ] URL Railway dicatat untuk Vercel

### Frontend Vercel
- [ ] Root Directory diset ke `frontend`
- [ ] `VITE_BACKEND_URL` diset ke URL Railway
- [ ] Build berhasil
- [ ] Login page bisa diakses
- [ ] API calls berhasil (Network tab browser)

### Media Storage
- [ ] R2/S3 bucket dibuat
- [ ] Public access diaktifkan
- [ ] `django-storages` dan `boto3` ditambahkan ke `requirements.txt`
- [ ] Settings `USE_S3=True` dan credentials diset di Railway
- [ ] Upload foto wajah berfungsi dan accessible via URL

### Post-Deploy
- [ ] `FRONTEND_URL` di Railway diupdate ke URL Vercel yang sebenarnya
- [ ] CORS tidak error di browser (Network tab)
- [ ] Login dengan local auth berhasil
- [ ] Face comparison berfungsi
- [ ] Media file bisa diakses setelah upload

---

## 6. Troubleshooting

### CORS Error di browser
Pastikan `FRONTEND_URL` di Railway sudah diset dan sama persis dengan URL Vercel (termasuk `https://` dan tanpa trailing slash).

### 500 Error saat login
Cek Railway logs. Kemungkinan `SECRET_KEY` belum diset atau database belum terhubung.

### Media tidak muncul setelah upload
Jika belum setup S3: file disimpan di container Railway yang ephemeral. Setup R2/S3 dulu.
Jika sudah setup S3: cek `AWS_S3_CUSTOM_DOMAIN` dan pastikan bucket public access aktif.

### Build Railway gagal karena torch/tensorflow terlalu besar
Railway punya limit 8GB disk saat build. `torch==2.2.2+cpu` ~700MB, `tensorflow-cpu` ~400MB — total masih aman. Jika tetap gagal, tambahkan di Railway:
```
NIXPACKS_NO_CACHE=true
```

### Vite build error di Vercel
Pastikan Root Directory di Vercel diset ke `frontend`, bukan root repo.

---

## 7. Arsitektur Flow

```
User Browser
    │
    ▼
Vercel CDN (frontend Vue)
    │  HTTPS request ke /api/*
    ▼
Railway (Django + DeepFace)
    │                    │
    ▼                    ▼
Railway MySQL      Cloudflare R2
(users, logs,      (face images,
 settings)          media files)
```
