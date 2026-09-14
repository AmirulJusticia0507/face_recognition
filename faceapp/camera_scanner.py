import logging
import uuid
import os
import time
from typing import Optional

import cv2
import numpy as np
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from django.core.files.base import ContentFile
from django.utils import timezone

from deepface import DeepFace

from .models import Camera, CameraScanLog, Person

logger = logging.getLogger(__name__)

CASCADE_PATH = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'


def _open_stream(stream_url, timeout=5):
    cap = cv2.VideoCapture(stream_url)
    if not cap.isOpened():
        return None, 'not_opened'
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    return cap, None


def _read_frame(cap, max_tries=10):
    for _ in range(max_tries):
        ret, frame = cap.read()
        if ret and frame is not None and frame.size > 0:
            return True, frame
        time.sleep(0.2)
    return False, None


def _dnn_faces(frame):
    model_files = []
    try:
        import os as _os
        data_dirs = [getattr(cv2.data, 'haarcascades', ''), getattr(cv2.data, 'samples', '')]
        for d in data_dirs:
            if d and _os.path.isdir(d):
                model_files.extend(_os.listdir(d))
    except Exception:
        pass
    model_files = [f for f in model_files if f.endswith('.xml') and 'frontalface' in f.lower()]
    if model_files:
        path = os.path.join(data_dirs[0], model_files[0])
        cascade = cv2.CascadeClassifier(path)
        if not cascade.empty():
            return cascade.detectMultiScale(frame, 1.3, 5)
    return np.array([]).reshape(0, 4)


def _detect_faces(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cascade = None
    if hasattr(cv2, 'CascadeClassifier'):
        try:
            cascade = cv2.CascadeClassifier(CASCADE_PATH)
        except cv2.error:
            cascade = None
    if cascade is not None and not cascade.empty():
        return cascade.detectMultiScale(gray, 1.3, 5), gray
    if hasattr(cv2, 'FaceDetectorYN_create'):
        return _dnn_faces(gray), gray
    return np.array([]).reshape(0, 4), gray


def _identify_face(frame, model_name, detector_backend, align):
    tmp = None
    try:
        suffix = uuid.uuid4().hex
        tmp_path = os.path.join(settings.MEDIA_ROOT, 'camera_scans', f'_id_{suffix}.jpg')
        os.makedirs(os.path.dirname(tmp_path), exist_ok=True)
        encoded, buf = cv2.imencode('.jpg', frame)
        if not encoded:
            return None
        with open(tmp_path, 'wb') as fh:
            fh.write(buf.tobytes())
        result = DeepFace.find(
            img_path=tmp_path,
            db_path=os.path.join(settings.MEDIA_ROOT, 'face_db'),
            model_name=model_name,
            detector_backend=detector_backend,
            enforce_detection=False,
            align=align,
            silent=True,
        )
        if not result or result[0].empty:
            return None
        df = result[0].sort_values('distance')
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
        threshold = float(best.get('threshold', 0.0)) if 'threshold' in best.index else 0.0
        distance = float(best['distance'])
        similarity = round((1 - distance / threshold) * 100, 2) if threshold > 0 else 0.0
        return {
            'person_id': person.id,
            'person_name': person.name,
            'similarity_percent': max(0.0, min(similarity, 100.0)),
        }
    except Exception as exc:
        logger.exception("DeepFace identification failed: %s", exc)
        return None
    finally:
        if tmp and os.path.exists(tmp):
            try:
                os.unlink(tmp)
            except OSError:
                pass


def detect_faces_in_frame(frame, model_name='ArcFace', detector_backend='opencv', align=True,
                          threshold=0.4, identify=True):
    faces, gray = _detect_faces(frame)
    face_count = int(len(faces))
    matched_person = None
    similarity = 0.0
    raw_result = {'face_count': face_count, 'faces': [list(map(int, f)) for f in faces]}

    if identify and face_count > 0:
        for (x, y, w, h) in faces:
            face_img = gray[y:y + h, x:x + w]
            face_rgb = cv2.cvtColor(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), cv2.COLOR_GRAY2BGR)
            face_rgb = frame[y:y + h, x:x + w]
            ident = _identify_face(face_rgb, model_name, detector_backend, align)
            if ident and ident['similarity_percent'] >= threshold:
                matched_person = ident
                similarity = ident['similarity_percent']
                raw_result['match'] = ident
                break

    return {
        'face_count': face_count,
        'face_detected': face_count > 0,
        'matched_person': matched_person,
        'similarity_percent': similarity,
        'raw_result': raw_result,
    }


def scan_camera(camera: Camera, identify: bool = True) -> Optional[CameraScanLog]:
    stream_url = camera.stream_url
    if not stream_url:
        return _save_error(camera, None, 'Camera tidak memiliki stream_url')

    cap, err = _open_stream(stream_url)
    if cap is None:
        return _save_error(camera, stream_url, f'Gagal membuka stream: {err}')

    try:
        ret, frame = _read_frame(cap)
        if not ret:
            return _save_error(camera, stream_url, 'Gagal membaca frame dari stream')
        _, buf = cv2.imencode('.jpg', frame)
        if not _:
            return _save_error(camera, stream_url, 'Gagal mengenkode frame')
        image_content = ContentFile(buf.tobytes(), name=f"scan_{camera.id}_{uuid.uuid4().hex}.jpg")

        from .api_views import get_active_face_config
        cfg = get_active_face_config()
        detection = detect_faces_in_frame(
            frame,
            model_name=cfg['model_name'],
            detector_backend=cfg['detector_backend'],
            align=cfg['align'],
            threshold=cfg['threshold'],
            identify=identify,
        )

        log = CameraScanLog.objects.create(
            camera=camera,
            camera_name=camera.name,
            building=camera.building,
            room=camera.room,
            floor=camera.floor,
            stream_url=stream_url,
            image=image_content,
            model_used=cfg['model_name'],
            detection_method='haar',
            face_detected=detection['face_detected'],
            face_count=detection['face_count'],
            similarity_percent=detection['similarity_percent'],
            raw_result=detection['raw_result'],
        )

        if detection['matched_person']:
            try:
                log.matched_person = Person.objects.get(pk=detection['matched_person']['person_id'])
                log.save(update_fields=['matched_person'])
            except Person.DoesNotExist:
                pass

        if log.face_detected:
            _broadcast_detection(log)
        camera.last_scanned_at = timezone.now()
        camera.save(update_fields=['last_scanned_at'])
        return log
    except Exception as exc:
        logger.exception("scan_camera error for %s", camera.name)
        return _save_error(camera, stream_url, str(exc))
    finally:
        cap.release()


def _save_error(camera: Camera, stream_url, error_message):
    try:
        log = CameraScanLog.objects.create(
            camera=camera,
            camera_name=camera.name,
            building=camera.building,
            room=camera.room,
            floor=camera.floor,
            stream_url=stream_url or '',
            image='camera_scans/placeholder.jpg',
            model_used='haar',
            detection_method='haar',
            face_detected=False,
            face_count=0,
            similarity_percent=0.0,
            raw_result={},
            error_message=error_message or 'Unknown error',
        )
        return log
    except Exception:
        logger.exception("failed saving error scan log")
        return None


def _broadcast_detection(log: CameraScanLog):
    payload = {
        'type': 'face.detected',
        'scan_id': log.id,
        'camera_id': log.camera_id,
        'camera_name': log.camera_name,
        'building': log.building,
        'room': log.room,
        'face_detected': log.face_detected,
        'face_count': log.face_count,
        'matched_person': {
            'id': p.id,
            'name': p.name,
        } if (p := log.matched_person) else None,
        'similarity_percent': log.similarity_percent,
        'timestamp': log.created_at.isoformat(),
    }
    try:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)('detection_notifications', payload)
    except Exception:
        logger.exception("broadcast_detection failed")
