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

## Tech Stack

- Python 3.12, Django 6
- DeepFace 0.0.100 (ArcFace, VGG-Face, Facenet, dll)
- OpenCV, TensorFlow, Torch, mtcnn
- MySQL (via pymysql)
- Django REST Framework

## Instalasi

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

## Catatan Penting

- **`opencv-python<5`** — OpenCV 5.x menghapus `CascadeClassifier` dan haarcascade dari wheel sehingga merusak deteksi wajah DeepFace.
- **`dlib` tidak dipakai** — tidak ada di requirements karena gagal build dari source di Windows tanpa cmake dan tidak diperlukan aplikasi ini.
- **Folder `venv/`, `media/face_db/`, `__pycache__/`** masuk `.gitignore` — tidak ikut di-push.
- Folder **`media/faces/`** (foto hasil unggahan) ikut ter-track di git.

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

## Lisensi

Hak milik proyek masing-masing.
