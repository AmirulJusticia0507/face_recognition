# FaceAI — Face Recognition

Aplikasi face recognition berbasis **Django** + **DeepFace** untuk verifikasi, identifikasi, dan pemantauan wajah.

## Fitur

- **Face Comparison** (`/`) — bandingkan 2 foto wajah menggunakan `DeepFace.verify`, lengkap dengan skor pose, pencahayaan, okulasi, dan ketajaman.
- **Identifikasi** (`/identify/`) — upload 1 foto untuk mencari tahu siapa orangnya di database menggunakan `DeepFace.find`.
- **Data Orang** (`/people/`) — daftar orang terdaftar, bisa dihapus.
- **Registrasi Wajah** (`/people/register/`) — daftarkan orang baru + upload banyak foto wajah (divalidasi otomatis wajahnya terdeteksi).
- **Live Camera** (`/live-camera/`) — kamera langsung + simpan snapshot.
- **Pose Estimation** (`/pose-estimation/`) — estimasi pose wajah (masih dummy).
- **ETLE Camera** (`/etle-camera/`) + **Violation Logs** (`/violation-logs/`) — pencatatan pelanggaran kendaraan.
- **History** (`/history/`) — riwayat perbandingan wajah.
- **Model Settings** (`/model-settings/`), **About** (`/about/`).
- **Admin Django** (`/admin/`) — semua model terdaftar.
- **SSO Login** — autentikasi via Keycloak SSO + Google Login.

## Tech Stack

### Backend
- Python 3.12, Django 6
- DeepFace 0.0.100 (ArcFace, VGG-Face, Facenet, dll)
- OpenCV, TensorFlow, Torch, mtcnn
- MySQL (via pymysql)
- Django REST Framework

### Frontend (`frontend/`)
- Vue.js 3 + Vite
- Tailwind CSS
- Vue Router 4
- Pinia (state management)
- Axios (HTTP client)
- Notivue (toast notifications)
- SweetAlert2
- Chart.js + vue-chartjs

## Instalasi

### Backend

```bash
# 1. Buat virtual environment
python -m venv venv

# 2. Aktifkan
venv\Scripts\activate

# 3. Install dependensi
pip install -r requirements.txt

# 4. Siapkan database MySQL
mysql -u root -e "CREATE DATABASE IF NOT EXISTS db_face_recognition CHARACTER SET utf8mb4"

# 5. Migrasi
python manage.py migrate

# 6. Jalankan server
python manage.py runserver
```

Buka http://127.0.0.1:8000

### Frontend

```bash
# 1. Masuk ke folder frontend
cd frontend

# 2. Install dependensi
npm install

# 3. Jalankan dev server
npm run dev
```

Buka http://localhost:5173

> Vite dev server otomatis proxy `/api` dan `/media` ke Django di `localhost:8000`.

### Konfigurasi SSO (opsional)

Buat file `frontend/.env` untuk konfigurasi SSO/Keycloak:

```env
VITE_SSO_TOKEN_URL=https://sso.jogjaprov.go.id/realms/aptika/protocol/openid-connect/token
VITE_SSO_USERINFO_URL=https://sso.jogjaprov.go.id/realms/aptika/protocol/openid-connect/userinfo
VITE_SSO_CLIENT_ID=webopd
VITE_SSO_CLIENT_ID_PORTAL=portal
VITE_SSO_SCOPE=openid
VITE_SSO_KEYCLOAK_BASE=https://sso.jogjaprov.go.id/realms/aptika/protocol/openid-connect
```

## Struktur Proyek

```
face_recognition/
├── core/                    # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── faceapp/                 # Aplikasi utama
│   ├── models.py            # FaceLog, FaceComparisonLog, Person, dll
│   ├── views.py             # View Django (template-based)
│   ├── urls.py
│   ├── forms.py
│   ├── serializers.py       # DRF serializers
│   ├── face_services.py     # Service layer (DeepFace)
│   ├── templates/           # Template HTML lama (Django)
│   └── migrations/
├── media/                   # File media
│   ├── faces/               # Foto wajah unggahan
│   ├── face_db/             # Database wajah DeepFace
│   └── snapshots/           # Snapshot kamera
├── frontend/                # Vue.js 3 SPA
│   ├── src/
│   │   ├── main.js          # Entry point + notivue
│   │   ├── App.vue          # Root component + OAuth callback
│   │   ├── router/          # Vue Router
│   │   ├── stores/          # Pinia stores (auth, sidebar)
│   │   ├── services/        # API services (api.js, sso.js)
│   │   ├── components/
│   │   │   └── layout/      # Sidebar, Header, Footer, MainLayout
│   │   ├── views/           # Halaman-halaman
│   │   └── assets/          # CSS + Tailwind
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── .env                 # Konfigurasi SSO
├── manage.py
├── requirements.txt
└── README.md
```

## Struktur Frontend

```
frontend/src/
├── components/layout/
│   ├── MainLayout.vue       # Wrapper: sidebar + header + content + footer
│   ├── Sidebar.vue          # Collapsible sidebar (w-64 / w-20)
│   ├── Header.vue           # Sticky header + user menu + notifikasi
│   └── Footer.vue           # Footer links + copyright
├── views/
│   ├── Dashboard.vue        # Overview stats + quick actions
│   ├── FaceComparison.vue   # Bandingkan 2 foto (drag & drop)
│   ├── Identify.vue         # Identifikasi wajah dari database
│   ├── People.vue           # Tabel data orang
│   ├── RegisterPerson.vue   # Form registrasi + upload foto
│   ├── History.vue          # Riwayat perbandingan
│   ├── ModelSettings.vue    # Konfigurasi model + threshold
│   ├── LiveCamera.vue       # Kamera real-time + snapshot
│   ├── PoseEstimation.vue   # Analisis kualitas pose wajah
│   ├── EtleCamera.vue       # ETLE camera + deteksi pelanggaran
│   ├── ViolationLogs.vue    # Log pelanggaran
│   ├── About.vue            # Info aplikasi
│   ├── Login.vue            # Login form + Google SSO
│   ├── Register.vue         # Registrasi akun
│   └── NotFound.vue         # 404 page
├── services/
│   ├── api.js               # Axios instance + API endpoints
│   └── sso.js               # SSO/Keycloak auth functions
├── stores/
│   ├── auth.js              # Auth state (user, token, login/logout)
│   └── sidebar.js           # Sidebar state (collapsed, mobile)
├── router/
│   └── index.js             # Routes + navigation guards
└── assets/
    └── main.css             # Tailwind + custom component classes
```

## Struktur Galeri Identifikasi

Foto wajah hasil registrasi disimpan per orang:

```
media/face_db/
  └── <person_id>/
        ├── <uuid>.jpg
        └── ...
```

`DeepFace.find` memindai folder ini secara rekursif; cache embedding dibuat otomatis oleh DeepFace.

## Endpoint API

- `POST /compare/` — upload `foto_a`, `foto_b`, `model` → hasil verifikasi + skor kualitas
- `POST /live-camera/save-snapshot/` — simpan snapshot kamera (base64)

## Catatan Penting

- **`opencv-python<5`** — OpenCV 5.x menghapus `CascadeClassifier` dan haarcascade dari wheel sehingga merusak deteksi wajah DeepFace.
- **`dlib` tidak dipakai** — tidak ada di requirements karena gagal build dari source di Windows tanpa cmake dan tidak diperlukan aplikasi ini.
- **Folder `venv/`, `media/face_db/`, `__pycache__/`** masuk `.gitignore` — tidak ikut di-push.
- Folder **`media/faces/`** (foto hasil unggahan) ikut ter-track di git.
- **`frontend/node_modules/`** dan **`frontend/dist/`** masuk `.gitignore`.

## Lisensi

Hak milik proyek masing-masing.
