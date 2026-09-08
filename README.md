# FaceAI — Face Recognition

Aplikasi face recognition berbasis **Django + DeepFace** (backend) dan **Vue 3** (frontend):
verifikasi wajah, identifikasi orang, estimasi pose, forensik citra, pemantauan kamera/ETLE,
manajemen model, serta roles & users.

## Fitur

### Pengenalan wajah
- **Face Comparison** — bandingkan 2 foto (`DeepFace.verify`) + skor kualitas
  (pose, lighting, occlusion, sharpness). Parameter (model, detection backend,
  enforce detection, align) diambil otomatis dari **Model Settings**.
- **Identify** — upload 1 foto untuk mencari kecocokan di database (`DeepFace.find`).
  Setiap percobaan (cocok maupun tidak) tercatat di log.
- **Data Orang & Registrasi Wajah** — CRUD orang, upload banyak foto sekaligus
  (otomatis divalidasi: wajah harus terdeteksi).
- **History** — riwayat perbandingan, detail, hapus satuan / hapus semua.

### Kualitas citra & forensik
- **Pose Estimation** — skor pose/lighting/occlusion/sharpness + skor keseluruhan.
  Hasilnya **disimpan** sebagai riwayat (`PoseLog`).
- **Forensic Analysis** — ELA, noise, sharpening, median filter, JPEG ghost,
  copy-move, dan metadata (hasil + log tersimpan).

### Kamera & pelanggaran
- **Live Camera** — snapshot kamera + daftar snapshot.
- **ETLE Camera** — daftar kamera statis + CCTV Jogja (live), deteksi pelanggaran dari frame.
- **Violation Logs** — daftar, detail, statistik, export CSV.
- **Camera Management** — CRUD kamera CCTV (nama, sumber, stream URL, koordinat, status).

### Pengaturan, dashboard, auth
- **Model Settings** — model default, similarity threshold, detection backend,
  enforce detection, align + uji kecepatan model.
- **Settings** — Roles (Django Groups + permissions) & User management (CRUD, toggle aktif).
- **Profile** — lihat/ubah profil + ganti password.
- **Dashboard** — statistik, aktivitas terkini, chart perbandingan.
- **Auth** — Token Authentication. Hanya `login`/`register` yang terbuka;
  seluruh endpoint lain wajib `Authorization: Token <token>`.
  Frontend juga mendukung SSO Keycloak (opsional).

## Tech Stack

### Backend
- Python 3.11 (deploy; lokal 3.13 juga jalan), Django 6.1.1, DRF 3.16
- DeepFace 0.0.93 — default ArcFace; tersedia Facenet, VGG-Face, OpenFace,
  DeepFace, DeepID, Dlib
- opencv-python-headless 4.10, torch **CPU-only** + tensorflow-cpu (hemat ukuran install)
- MySQL via pymysql; `django-storages` + boto3 untuk media S3/R2 (production)
- gunicorn + whitenoise (production)

### Frontend (`frontend/`)
- Vue 3 + Vite, Tailwind CSS, Vue Router 4, Pinia, Axios
- Leaflet (peta kamera), Chart.js + vue-chartjs, SweetAlert2, Notivue

### Type checking (dev)
- `django-stubs` + `djangorestframework-stubs`, Pyrefly dengan `pyrefly.toml`
  yang mengarah ke `venv/` project.

## Instalasi Lokal

### Backend

```bash
# 1. Buat & aktifkan virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

# 2. Install dependensi (versi ter-pin, CPU-only torch)
pip install -r requirements.txt

# 3. (Opsional, untuk develop) dependensi tambahan lokal
pip install -r requirements-dev.txt

# 4. Siapkan database MySQL
mysql -u root -e "CREATE DATABASE IF NOT EXISTS db_face_recognition CHARACTER SET utf8mb4"

# 5. Migrasi + buat admin
python manage.py migrate
python manage.py createsuperuser

# 6. Jalankan server
python manage.py runserver
```

Buka http://127.0.0.1:8000 — API tersedia di `http://127.0.0.1:8000/api/`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Buka http://localhost:5173. Vite mem-proxy `/api` dan `/media` ke backend
(`VITE_BACKEND_URL`, default `http://localhost:8000`), jadi `VITE_BACKEND_URL`
tidak perlu diset saat develop lokal.

## Environment Variables

### Backend (Railway / production via dashboard; lokal via `.env` / shell)

| Variable | Wajib | Keterangan |
|---|---|---|
| `SECRET_KEY` | Ya (prod) | Random panjang. Default dev hanya untuk lokal |
| `DEBUG` | Ya (prod) | `False` di production |
| `MYSQL_HOST/PORT/USER/PASSWORD/DATABASE` | Ya | Otomatis dari plugin MySQL Railway |
| `FRONTEND_URL` | Ya (prod) | URL Vercel, untuk CORS + CSRF |
| `RAILWAY_PUBLIC_DOMAIN` | Otomatis | Di-inject Railway, untuk `ALLOWED_HOSTS` |
| `USE_S3` | Ya (prod) | `True` → media disimpan di S3/R2, bukan filesystem ephemeral |
| `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` | Ya (prod) | Kredensial R2/S3 |
| `AWS_STORAGE_BUCKET_NAME` | Ya (prod) | Mis. `face-recognition-media` |
| `AWS_S3_ENDPOINT_URL` | Ya (R2/B2) | Mis. `https://<account>.r2.cloudflarestorage.com` |
| `AWS_S3_CUSTOM_DOMAIN` | Anjuran | Public domain bucket (mis. `pub-xxxx.r2.dev`) |

### Frontend (Vercel → Settings → Environment Variables)

| Variable | Keterangan |
|---|---|
| `VITE_BACKEND_URL` | URL backend Railway (mis. `https://xxx.up.railway.app`). Jika kosong, axios memakai path relatif `/api` |
| `VITE_API_URL` | Base AI-CCTV eksternal + SSO portal (lihat `.env.production`) |
| `VITE_SSO_*` / `VITE_KEYCLOAK_*` | Konfigurasi SSO/Keycloak JogjaProv |
| `VITE_MAPBOX_ACCESS_TOKEN` | Token Mapbox untuk peta. **Isi via dashboard Vercel, jangan commit token asli** |

> ⚠️ Jangan pernah commit token/kredensial asli ke repo. GitHub Push Protection
> menolak push yang mengandung secret (pernah kejadian dengan Mapbox token di
> `frontend/.env.production` — di repo hanya boleh ada placeholder).

## Endpoint API

Base URL: `/api/`. Kecuali login/register, semua butuh header
`Authorization: Token <token>`.

| Method | Path | Keterangan |
|---|---|---|
| POST | `/auth/login/`, `/auth/register/` | Login / registrasi (terbuka) |
| POST | `/auth/logout/` | Hapus token |
| GET/PUT | `/auth/profile/` | Profil user |
| POST | `/auth/change-password/` | Ganti password |
| GET | `/dashboard/stats/`, `/dashboard/recent-activity/`, `/dashboard/charts/` | Statistik & chart |
| GET/POST | `/people/` | List (search + pagination) / tambah orang |
| GET/PUT/DELETE | `/people/<id>/` | Detail / ubah / hapus |
| POST | `/people/<id>/upload-photos/` | Upload banyak foto (`photos`) |
| GET/DELETE | `/people/<id>/photos/`[+`/<photo_id>/`] | List / hapus foto |
| POST | `/face-compare/` | Bandingkan `foto_a` + `foto_b` (`model` opsional, default dari settings) |
| GET/DELETE | `/face-comparison/history/`, `/face-comparison/<id>/`, `/history/...` | Riwayat + hapus + clear |
| POST | `/identify/` | Identifikasi dari `photo` (log otomatis tersimpan) |
| GET | `/identify/models/` | Daftar model tersedia |
| GET/PUT | `/model-settings/` | Baca / ubah pengaturan model |
| GET | `/model-settings/available/` | Daftar model |
| POST | `/model-settings/test/` | Uji kecepatan model |
| POST/GET/DELETE | `/live-camera/snapshot/`, `/live-camera/snapshots/`[+`/<id>/`] | Snapshot kamera |
| POST/GET | `/pose-estimation/`, `/pose-estimation/history/` | Estimasi pose + riwayat |
| GET | `/etle-camera/cameras/`, `/etle-camera/cameras/jogja/` | Kamera statis / CCTV Jogja live |
| POST | `/etle-camera/detect/` | Deteksi dari gambar / stream |
| GET/POST/PUT/DELETE | `/cameras/`, `/cameras/<id>/` | CRUD kamera CCTV |
| GET/DELETE | `/violation-logs/`, `/violation-logs/stats/`, `/violation-logs/<id>/` | Log pelanggaran |
| POST/GET | `/forensic/ela/` | Analisis forensik (`image` + `method`) + riwayat |
| GET/POST | `/roles/`, `/roles/<id>/`, `/permissions/` | Roles & permissions |
| GET/POST/PUT/DELETE | `/users/`, `/users/<id>/`, `/users/<id>/toggle-active/` | User management |

## Struktur Proyek

```
face_recognition/
├── core/                      # Django project (settings, urls, wsgi)
├── faceapp/                   # Aplikasi utama
│   ├── api_views.py           # Semua DRF API views (auth wajib kecuali login/register)
│   ├── api_urls.py            # Routing /api/*
│   ├── face_services.py       # DeepFace: verify/find, validasi & simpan foto
│   ├── forensics/             # ELA, noise, sharpening, ghost, copy-move, metadata
│   ├── models.py              # Person, FaceImage, FaceComparisonLog, FaceLog,
│   │                          # PoseLog, ViolationLog, ForensicLog, ModelSetting, Camera
│   ├── serializers.py
│   ├── views.py / urls.py / forms.py  # View Django lama (template-based)
│   └── migrations/
├── frontend/                  # Vue 3 SPA
│   ├── src/
│   │   ├── views/             # Dashboard, FaceComparison, Identify, People,
│   │   │                      # PersonDetail, RegisterPerson, History, ModelSettings,
│   │   │                      # LiveCamera, PoseEstimation, EtleCamera, ViolationLogs,
│   │   │                      # CameraManagement, ForensicAnalysis, Settings,
│   │   │                      # Profile, Login, Register, About, NotFound
│   │   ├── services/api.js    # Axios + semua grup API (otomatis pakai VITE_BACKEND_URL)
│   │   ├── services/sso.js    # Keycloak SSO
│   │   ├── stores/            # Pinia: auth, sidebar
│   │   ├── router/            # Routes + navigation guards
│   │   └── assets/            # Tailwind + CSS
│   ├── vite.config.js         # Proxy /api & /media ke VITE_BACKEND_URL / localhost:8000
│   ├── vercel.json            # SPA rewrite rules (Vercel)
│   └── .env.production        # Fallback env production (TANPA secret asli)
├── media/                     # faces/, snapshots/, pose_snapshots/, forensic/, violations/
│                              # face_db/ = galeri DeepFace per <person_id>/ (di-gitignore)
├── Procfile / railway.toml / runtime.txt / .python-version  # Deploy Railway (Python 3.11)
├── requirements.txt           # Dependensi ter-pin (torch CPU-only)
├── requirements-dev.txt       # Tambahan khusus develop lokal
├── pyrefly.toml               # Type checker → venv project
├── DEPLOYMENT.md              # Panduan deploy Railway + Vercel + R2
└── README.md
```

### Struktur galeri identifikasi

```
media/face_db/
  └── <person_id>/
        ├── <uuid>.jpg
        └── ...
```

`DeepFace.find` memindai folder ini secara rekursif; cache embedding dibuat otomatis DeepFace.

## Deployment

Panduan lengkap (Railway backend + MySQL + R2 media, Vercel frontend, checklist,
troubleshooting) ada di **[DEPLOYMENT.md](DEPLOYMENT.md)**.

## Catatan Penting

- **`opencv-python-headless`** dipakai (bukan `opencv-python`) agar install server
  ringan tanpa dependensi GUI; `cv2.data.haarcascades` tetap tersedia.
- **Torch CPU-only + tensorflow-cpu** — full GPU build ~800MB dan tidak perlu
  untuk inference DeepFace di server ini.
- **`dlib` tidak dipakai** — gagal build dari source di Windows tanpa cmake dan
  tidak dibutuhkan aplikasi ini.
- **Yang masuk `.gitignore`**: `venv/`, `__pycache__/`, `.env`, `db.sqlite3`,
  `staticfiles/`, `media/face_db/`, `frontend/node_modules/`, `frontend/dist/`.
  Foto hasil unggahan (`media/faces/`) ikut ter-track.
- **Ephemeral filesystem**: di Railway, file upload hilang saat restart —
  production wajib `USE_S3=True` (Cloudflare R2/S3).
- **Type checking**: install `django-stubs` + `djangorestframework-stubs` di venv
  agar Pyrefly (via `pyrefly.toml`) tidak false-positive pada ORM Django.

## Lisensi

Hak milik proyek masing-masing.
