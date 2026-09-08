# Deployment Guide

Arsitektur deployment split:
- **Frontend (Vue 3)** → Vercel (static hosting)
- **Backend (Django)** → Railway (persistent container)
- **Database** → Railway MySQL plugin
- **Media Storage** → Cloudflare R2 / AWS S3 (**wajib** — Railway filesystem ephemeral)

---

## Status Kesiapan Repo

| Komponen | Status | Keterangan |
|---|---|---|
| `Procfile` | ✅ Siap | gunicorn entry point |
| `railway.toml` | ✅ Siap | build + start command |
| `runtime.txt` / `.python-version` | ✅ Siap | Python 3.11 |
| `requirements.txt` | ✅ Siap | cpu-only torch, pinned versions |
| `core/settings.py` | ✅ Siap | baca env vars untuk DB, SECRET_KEY, CORS |
| `frontend/vercel.json` | ✅ Siap | SPA rewrite rules |
| `frontend/vite.config.js` | ✅ Siap | proxy via `VITE_BACKEND_URL` |
| `frontend/src/services/api.js` | ✅ Siap | absolute URL ke Railway jika env set |
| **`django-storages` + S3 config** | ✅ Sudah | Di `requirements.txt` + blok `USE_S3` di `core/settings.py` |

> Media storage sudah terimplementasi. Tinggal setup bucket R2 dan set env vars di Railway (section 3).

---

## Prasyarat

- Akun [Railway](https://railway.app)
- Akun [Vercel](https://vercel.com)
- Akun [Cloudflare](https://cloudflare.com) (untuk R2 storage — gratis)
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

## 3. Setup Media Storage (Wajib — Lakukan Sebelum Deploy)

> **Masalah:** Railway menggunakan ephemeral filesystem — semua file yang diupload (foto wajah, forensik, snapshot) **akan hilang** saat redeploy atau restart. Ini bukan opsional untuk sistem face recognition.

### Pilihan Storage

| Pilihan | Harga | Kemudahan |
|---|---|---|
| **Cloudflare R2** | Free 10GB/bulan, $0.015/GB setelahnya | ⭐⭐⭐ Rekomendasi |
| **Backblaze B2** | Free 10GB | ⭐⭐⭐ |
| **AWS S3** | ~$0.023/GB | ⭐⭐ |

### 3.1 Kode di Repo (Sudah Ada — Tinggal Verifikasi)

Blok storage sudah terimplementasi di `core/settings.py` (cari `USE_S3`) dan
`django-storages[s3]` + `boto3` sudah ada di `requirements.txt`. Bentuknya:

```python
# ─── MEDIA STORAGE (S3-compatible: AWS S3 / Cloudflare R2 / Backblaze B2) ────
if os.environ.get('USE_S3') == 'True':
    INSTALLED_APPS += ['storages']

    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME', 'face-recognition-media')
    AWS_S3_ENDPOINT_URL = os.environ.get('AWS_S3_ENDPOINT_URL')   # R2/B2 endpoint
    AWS_S3_CUSTOM_DOMAIN = os.environ.get('AWS_S3_CUSTOM_DOMAIN') # Public domain R2
    AWS_DEFAULT_ACL = 'public-read'
    AWS_S3_FILE_OVERWRITE = False
    AWS_QUERYSTRING_AUTH = False  # URL publik tanpa signature

    if AWS_S3_CUSTOM_DOMAIN:
        MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/'
    elif AWS_S3_ENDPOINT_URL and AWS_STORAGE_BUCKET_NAME:
        MEDIA_URL = f'{AWS_S3_ENDPOINT_URL}/{AWS_STORAGE_BUCKET_NAME}/'
```

> Tanpa `USE_S3=True`, Django memakai filesystem lokal (`MEDIA_ROOT`) — cocok
> untuk develop lokal, tapi file hilang saat Railway restart/redeploy.

Setelah ini, lanjut ke setup Cloudflare R2 dan deploy Railway.

---

### 3.2 Setup Cloudflare R2

1. Login ke [dash.cloudflare.com](https://dash.cloudflare.com) → **R2 Object Storage**
2. **Create bucket** → nama: `face-recognition-media` → lokasi: Auto
3. Di bucket → **Settings** → **Public Access** → **Allow Access** → konfirmasi
4. Catat **Public Bucket URL** yang muncul, contoh: `https://pub-xxxx.r2.dev`
5. Kembali ke halaman R2 utama → **Manage R2 API Tokens** → **Create API Token**
   - Permission: `Object Read & Write`
   - Scope: `Specific bucket` → pilih `face-recognition-media`
   - Klik **Create API Token**
6. Catat semua nilai yang muncul (hanya tampil sekali):
   - **Access Key ID**
   - **Secret Access Key**
   - **Endpoint**: `https://<account_id>.r2.cloudflarestorage.com`

### 3.3 Set Environment Variables R2 di Railway

Di service Django → tab **Variables**, tambahkan:

| Variable | Nilai |
|---|---|
| `USE_S3` | `True` |
| `AWS_ACCESS_KEY_ID` | Access Key ID dari R2 |
| `AWS_SECRET_ACCESS_KEY` | Secret Access Key dari R2 |
| `AWS_STORAGE_BUCKET_NAME` | `face-recognition-media` |
| `AWS_S3_ENDPOINT_URL` | `https://<account_id>.r2.cloudflarestorage.com` |
| `AWS_S3_CUSTOM_DOMAIN` | `pub-xxxx.r2.dev` (dari langkah 3.2 poin 4) |

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
VITE_MAPBOX_ACCESS_TOKEN=(isi via Vercel env vars — jangan commit token asli)
```

---

## 5. Checklist Deployment

> Urutan pengerjaan yang benar: **Kode dulu → Railway → Vercel → Update CORS**

### Langkah 0 — Persiapan Kode (Sudah Selesai di Repo)
- [x] `django-storages[s3]==1.14.4` dan `boto3==1.35.0` ada di `requirements.txt`
- [x] Blok S3 storage config ada di `core/settings.py` (flag `USE_S3`)
- [x] Commit dan push ke GitHub

### Langkah 1 — Setup Cloudflare R2
- [ ] Bucket `face-recognition-media` dibuat
- [ ] Public access diaktifkan
- [ ] API Token dibuat (Object Read & Write)
- [ ] Access Key ID, Secret Key, Endpoint, Public Domain dicatat

### Langkah 2 — Deploy Backend Railway
- [ ] Project dibuat dari GitHub repo
- [ ] MySQL plugin ditambahkan dan terhubung
- [ ] `SECRET_KEY` diset (bukan default insecure key)
- [ ] `DEBUG=False` diset
- [ ] R2 env vars diset (`USE_S3`, `AWS_*`)
- [ ] `FRONTEND_URL` diisi sementara (update setelah Vercel)
- [ ] Build berhasil (cek logs Railway)
- [ ] Migrasi berjalan otomatis
- [ ] Superuser dibuat via Railway Shell: `python manage.py createsuperuser`
- [ ] URL Railway dicatat

### Langkah 3 — Deploy Frontend Vercel
- [ ] Root Directory diset ke `frontend`
- [ ] `VITE_BACKEND_URL` diset ke URL Railway
- [ ] Build berhasil
- [ ] URL Vercel dicatat

### Langkah 4 — Update CORS
- [ ] `FRONTEND_URL` di Railway diupdate ke URL Vercel yang sebenarnya
- [ ] Railway redeploy otomatis (atau trigger manual)

### Verifikasi Akhir
- [ ] Login berhasil (Network tab: POST `/api/auth/login/` → 200)
- [ ] CORS tidak error di browser console
- [ ] Upload foto wajah berhasil dan foto tampil (bukan broken image)
- [ ] Face comparison berfungsi
- [ ] Dashboard chart tampil data

### (Opsional) Seed Akun + Data Demo

Untuk presentasi, seed akun demo + data contoh via Railway Shell:

```bash
python manage.py seed_demo
```

Yang dibuat (idempotent, aman dijalankan ulang):
- User `demo` / password `demo12345` (staff, bukan superuser).
  Password custom: `python manage.py seed_demo --password <pass>`
- 4 orang contoh + foto wajah (diunduh dari randomuser.me — butuh internet).
- 3 contoh violation agar dashboard & halaman pelanggaran tidak kosong.

Login di URL Vercel dengan akun demo tersebut. Setelah demo selesai, hapus akunnya:

```bash
python manage.py shell -c "from django.contrib.auth.models import User; User.objects.filter(username='demo').delete()"
```

---

## 6. Troubleshooting

### CORS Error di browser
Pastikan `FRONTEND_URL` di Railway sudah diset dan sama persis dengan URL Vercel (termasuk `https://` dan tanpa trailing slash).

### 500 Error saat login
Cek Railway logs. Kemungkinan `SECRET_KEY` belum diset atau database belum terhubung.

### Media tidak muncul setelah upload
- **Jika `USE_S3` belum diset:** file disimpan di filesystem Railway yang ephemeral — setup R2 dulu (section 3).
- **Jika sudah `USE_S3=True`:** cek `AWS_S3_CUSTOM_DOMAIN` sudah benar dan bucket public access aktif.
- Cek Railway logs untuk error `NoCredentialsError` atau `BucketNotFound`.

### `ModuleNotFoundError: No module named 'storages'`
`django-storages` sudah ada di `requirements.txt` — error ini berarti build
Railway memakai cache lama. Tambahkan variable di Railway dan redeploy:
```
NIXPACKS_NO_CACHE=true
```

### Build Railway gagal karena memory/disk penuh
`torch==2.2.2+cpu` ~700MB + `tensorflow-cpu` ~400MB — total ~1.5GB saat install. Railway punya limit 8GB, masih aman. Jika tetap gagal, coba tambahkan variable di Railway:
```
NIXPACKS_NO_CACHE=true
```

### Vite build error di Vercel: `Cannot find module`
Pastikan Root Directory di Vercel diset ke `frontend`, bukan root repo.

### Login berhasil tapi semua API return 401
Token format salah. Pastikan tidak ada session SSO aktif yang konflik — coba clear localStorage browser lalu login ulang.

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
