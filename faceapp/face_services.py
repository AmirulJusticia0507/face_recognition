import os
import tempfile
import uuid

from django.conf import settings
from django.core.files.base import ContentFile

from deepface import DeepFace

from .models import FaceImage, Person

GALLERY_DIR = os.path.join(settings.MEDIA_ROOT, 'face_db')


def _gallery_dir():
    return GALLERY_DIR


def face_db_has_images():
    if not os.path.isdir(GALLERY_DIR):
        return False
    for _, _, files in os.walk(GALLERY_DIR):
        if any(f.lower().endswith(('.jpg', '.jpeg', '.png')) for f in files):
            return True
    return False


def validate_face(image_path, detector_backend='opencv'):
    faces = DeepFace.extract_faces(
        img_path=image_path,
        detector_backend=detector_backend,
    )
    return len(faces) > 0


def save_face_image(person, upload, detector_backend='opencv'):
    tmp = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
    tmp_path = tmp.name
    try:
        for chunk in upload.chunks():
            tmp.write(chunk)
        tmp.close()

        if not validate_face(tmp_path, detector_backend):
            return False, 'Tidak ada wajah terdeteksi di foto ini.'

        ext = os.path.splitext(upload.name)[1].lower()
        if ext not in ('.jpg', '.jpeg', '.png'):
            ext = '.jpg'
        filename = f"{uuid.uuid4().hex}{ext}"

        with open(tmp_path, 'rb') as fh:
            data = fh.read()

        FaceImage.objects.create(person=person, image=ContentFile(data, name=filename))
        return True, None
    except Exception as e:
        return False, str(e)
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def find_best_match(image_path, model_name='ArcFace', detector_backend='opencv'):
    if not face_db_has_images():
        return None

    dfs = DeepFace.find(
        img_path=image_path,
        db_path=GALLERY_DIR,
        model_name=model_name,
        detector_backend=detector_backend,
        silent=True,
    )
    if not dfs or dfs[0].empty:
        return None

    df = dfs[0].sort_values('distance')
    best = df.iloc[0]

    identity = str(best['identity']).replace('\\', '/')
    parts = identity.rstrip('/').split('/')
    try:
        person_id = int(parts[-2])
    except (ValueError, IndexError):
        return None

    try:
        person = Person.objects.get(pk=person_id)
    except Person.DoesNotExist:
        return None

    distance = float(best['distance'])
    threshold = float(best.get('threshold', 0.0)) if 'threshold' in best.index else 0.0
    if threshold > 0:
        similarity = round((1 - distance / threshold) * 100, 2)
    else:
        similarity = 0.0

    return {
        'person': person,
        'distance': distance,
        'threshold': threshold,
        'similarity_percent': max(0.0, min(similarity, 100.0)),
        'matched_image': identity,
    }
