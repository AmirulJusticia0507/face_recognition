"""Seed akun + data demo untuk presentasi (idempotent, aman dijalankan ulang).

Jalankan di Railway Shell (atau lokal):

    python manage.py seed_demo
    python manage.py seed_demo --password Demo1234   # password custom

Yang dibuat:
  - User `demo` (staff, bukan superuser) untuk login ke aplikasi/Vercel.
  - 4 orang contoh + masing-masing 1 foto wajah asli (diunduh dari
    randomuser.me — butuh koneksi internet saat seeding).
  - 3 contoh ViolationLog agar halaman dashboard & pelanggaran tidak kosong.
  - Memastikan satu baris ModelSetting ada (default aplikasi).

Setelah demo selesai, hapus akun demo:

    python manage.py shell -c "from django.contrib.auth.models import User; User.objects.filter(username='demo').delete()"
"""

import requests
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from faceapp.models import FaceImage, ModelSetting, Person, ViolationLog

DEMO_USERNAME = "demo"
DEMO_PASSWORD_DEFAULT = "demo12345"

# Potret wajah asli (CC0-ish, umum dipakai untuk mockup/demo).
DEMO_PEOPLE = [
    {"name": "Budi Santoso", "identifier": "DEMO-001", "email": "budi.demo@example.com", "photo": "https://randomuser.me/api/portraits/men/32.jpg"},
    {"name": "Siti Rahayu", "identifier": "DEMO-002", "email": "siti.demo@example.com", "photo": "https://randomuser.me/api/portraits/women/44.jpg"},
    {"name": "Agus Wijaya", "identifier": "DEMO-003", "email": "agus.demo@example.com", "photo": "https://randomuser.me/api/portraits/men/54.jpg"},
    {"name": "Dewi Lestari", "identifier": "DEMO-004", "email": "dewi.demo@example.com", "photo": "https://randomuser.me/api/portraits/women/68.jpg"},
]

DEMO_VIOLATIONS = [
    {"plate_number": "AB 1234 CD", "violation_type": "helmet", "location": "Simpang KM Nol", "camera_name": "Simpang KM Nol (PTZ)", "status": "Pending"},
    {"plate_number": "AB 5678 EF", "violation_type": "red_light", "location": "Simpang APMD", "camera_name": "Simpang APMD (PTZ)", "status": "Pending"},
    {"plate_number": "AB 9012 GH", "violation_type": "speeding", "location": "Simpang Sentul", "camera_name": "Simpang Sentul (PTZ)", "status": "Resolved"},
]


class Command(BaseCommand):
    help = "Seed akun demo (demo/demo12345) + data contoh untuk presentasi."

    def add_arguments(self, parser):
        parser.add_argument(
            "--password", default=DEMO_PASSWORD_DEFAULT,
            help=f"Password akun demo (default: {DEMO_PASSWORD_DEFAULT})",
        )

    def handle(self, *args, **options):
        password = options["password"]

        user, created = User.objects.get_or_create(
            username=DEMO_USERNAME,
            defaults={"email": "demo@example.com", "first_name": "Demo", "is_staff": True},
        )
        user.set_password(password)
        user.is_active = True
        user.is_staff = True
        user.save()
        self.stdout.write(self.style.SUCCESS(
            f"User demo: {DEMO_USERNAME} ({'dibuat' if created else 'password di-reset'})"
        ))

        ModelSetting.get_solo()

        for entry in DEMO_PEOPLE:
            person, _ = Person.objects.get_or_create(
                identifier=entry["identifier"],
                defaults={"name": entry["name"], "email": entry["email"]},
            )
            if person.face_images.exists():
                self.stdout.write(f"  - {person.name}: foto sudah ada, lewati")
                continue
            try:
                resp = requests.get(entry["photo"], timeout=20)
                resp.raise_for_status()
                FaceImage.objects.create(
                    person=person,
                    image=ContentFile(resp.content, name=f"{entry['identifier'].lower()}.jpg"),
                )
                self.stdout.write(f"  - {person.name}: foto tersimpan")
            except Exception as e:  # offline / URL mati -> orang tetap ada tanpa foto
                self.stdout.write(self.style.WARNING(f"  - {person.name}: foto gagal ({e})"))

        existing_plates = set(ViolationLog.objects.values_list("plate_number", flat=True))
        for v in DEMO_VIOLATIONS:
            if v["plate_number"] not in existing_plates:
                ViolationLog.objects.create(
                    plate_number=v["plate_number"],
                    violation_type=v["violation_type"],
                    location=v["location"],
                    camera_name=v["camera_name"],
                    description=f"Contoh data demo ({v['violation_type']})",
                    status=v["status"],
                )
        self.stdout.write(self.style.SUCCESS("Seed demo selesai."))
        self.stdout.write(f"Login dengan username `{DEMO_USERNAME}` / password yang diset.")
