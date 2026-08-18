import os
import uuid
import base64
import json
import tempfile

import cv2
import numpy as np
from django.utils import timezone
from django.http import JsonResponse
from django.core.files.base import ContentFile
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from django.views.generic import ListView, TemplateView
from .models import FaceLog, FaceComparisonLog, ViolationLog, Person, ForensicLog
from .forms import PersonForm
from .serializers import FaceComparisonLogSerializer
from . import face_services
from .forensics import analyze_ela, analyze_noise, analyze_sharpening, analyze_median_filter, analyze_jpeg_ghost, analyze_copy_move
from deepface import DeepFace

# Dummy pose score function
def calculate_pose_score_from_angle(pitch, yaw, roll):
    max_angle = 30
    score = max(0, 100 - (abs(pitch) + abs(yaw) + abs(roll)) / (3 * max_angle) * 100)
    return int(score)

# Dummy function for pose estimation (replace with actual model)
def estimate_pose_and_scores(face_path):
    # Dummy angles
    pitch, yaw, roll = 5, 3, 2
    pose_score = calculate_pose_score_from_angle(pitch, yaw, roll)

    face_image = cv2.imread(face_path)
    gray = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)

    # Lighting score
    brightness = np.mean(gray)
    lighting_score = int(np.clip((brightness / 255) * 100, 0, 100))

    # Occlusion score (dummy confidence)
    face_detection_confidence = 0.87
    occlusion_score = int(face_detection_confidence * 100)

    # Sharpness score
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    sharpness_score = min(int(laplacian_var / 100 * 100), 100)

    return pose_score, lighting_score, occlusion_score, sharpness_score

class FaceCompareView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request, *args, **kwargs):
        foto_a = request.FILES.get('foto_a')
        foto_b = request.FILES.get('foto_b')
        model_name = request.data.get('model', 'ArcFace')

        if not foto_a or not foto_b:
            return Response({"error": "Kedua foto wajib diunggah."}, status=400)

        foto_a_name = f"{uuid.uuid4()}_a.jpg"
        foto_b_name = f"{uuid.uuid4()}_b.jpg"
        foto_a_path = os.path.join(settings.MEDIA_ROOT, 'faces', foto_a_name)
        foto_b_path = os.path.join(settings.MEDIA_ROOT, 'faces', foto_b_name)
        os.makedirs(os.path.dirname(foto_a_path), exist_ok=True)

        with open(foto_a_path, 'wb+') as f:
            for chunk in foto_a.chunks():
                f.write(chunk)
        with open(foto_b_path, 'wb+') as f:
            for chunk in foto_b.chunks():
                f.write(chunk)

        try:
            result = DeepFace.verify(foto_a_path, foto_b_path, model_name=model_name)
            similarity = result.get("distance")
            threshold = result.get("threshold")
            verified = result.get("verified")
            similarity_percent = round((1 - similarity / threshold) * 100, 2)

            # Tambahan skor-skor
            pose_score, lighting_score, occlusion_score, sharpness_score = estimate_pose_and_scores(foto_a_path)

            log = FaceComparisonLog.objects.create(
                foto_a=f'faces/{foto_a_name}',
                foto_b=f'faces/{foto_b_name}',
                model_used=model_name,
                similarity_percent=similarity_percent,
                verified=verified
                # Jika ingin menyimpan skor tambahan, tambahkan di model dan simpan di sini
            )

            serializer = FaceComparisonLogSerializer(log)

            return Response({
                "match": verified,
                "similarity_percent": similarity_percent,
                "model_used": model_name,
                "pose_score": pose_score,
                "lighting_score": lighting_score,
                "occlusion_score": occlusion_score,
                "sharpness_score": sharpness_score,
                "data": serializer.data
            })

        except Exception as e:
            return Response({
                "error": "Gagal memproses gambar. Pastikan gambar jelas dan mengandung wajah.",
                "details": str(e)
            }, status=500)

class HistoryView(ListView):
    model = FaceComparisonLog
    template_name = 'faceapp/history.html'
    context_object_name = 'logs'
    ordering = ['-created_at']

class ModelSettingsView(TemplateView):
    template_name = 'faceapp/model-settings.html'

class AboutView(TemplateView):
    template_name = 'faceapp/about.html'

class LiveCameraView(TemplateView):
    template_name = 'faceapp/live-camera.html'

def face_form_view(request):
    return render(request, 'faceapp/index.html')

@csrf_exempt
def save_snapshot(request):
    if request.method == "POST":
        data = json.loads(request.body)
        image_data = data["image_base64"].split(',')[1]
        expression = data.get("detected_expression", "")
        image_file = ContentFile(base64.b64decode(image_data), name="snapshot.jpg")

        FaceLog.objects.create(
            foto_a=image_file,
            model_used="Live-Cam",
            similarity_percent=0,
            verified=False,
            created_at=timezone.now(),
            notes=expression
        )

        return JsonResponse({"status": "ok"})

def pose_estimation(request):
    return render(request, 'faceapp/pose-estimation.html')

def etle_camera(request):
    return render(request, 'faceapp/etle_camera.html')

def violation_logs(request):
    logs = ViolationLog.objects.all().order_by('-violation_time')
    return render(request, 'faceapp/violation_logs.html', {'logs': logs})


class PersonListView(ListView):
    model = Person
    template_name = 'faceapp/people.html'
    context_object_name = 'people'
    ordering = ['-created_at']


def register_person(request):
    if request.method == 'POST':
        form = PersonForm(request.POST)
        photos = request.FILES.getlist('photos')

        if form.is_valid() and photos:
            person = form.save()
            saved = 0
            errors = []
            for photo in photos:
                ok, err = face_services.save_face_image(person, photo)
                if ok:
                    saved += 1
                else:
                    errors.append(f"{photo.name}: {err}")

            if saved == 0:
                person.delete()
                form.add_error(None, 'Tidak ada foto valid. ' + ' | '.join(errors))
                return render(request, 'faceapp/register_person.html', {'form': form})

            messages.success(request, f'Registrasi berhasil: {saved} foto wajah disimpan untuk {person.name}.')
            if errors:
                messages.warning(request, 'Beberapa foto dilewati: ' + ' | '.join(errors))
            return redirect('people')

        if not photos:
            form.add_error(None, 'Minimal unggah satu foto wajah.')
        return render(request, 'faceapp/register_person.html', {'form': form})

    return render(request, 'faceapp/register_person.html', {'form': PersonForm()})


def identify(request):
    result = None
    error = None

    if request.method == 'POST':
        photo = request.FILES.get('photo')
        model_name = request.POST.get('model', 'ArcFace')

        if not photo:
            error = 'Foto wajib diunggah.'
        else:
            tmp = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
            tmp_path = tmp.name
            try:
                for chunk in photo.chunks():
                    tmp.write(chunk)
                tmp.close()

                result = face_services.find_best_match(tmp_path, model_name=model_name)
                if result is None:
                    error = 'Tidak ada kecocokan wajah di database.'
            except Exception as e:
                error = f'Gagal memproses gambar: {e}'
            finally:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)

    return render(request, 'faceapp/identify.html', {'result': result, 'error': error})


@require_POST
def delete_person(request, pk):
    person = Person.objects.filter(pk=pk).first()
    if person:
        person.delete()
        messages.success(request, f'{person.name} berhasil dihapus.')
    return redirect('people')


class ForensicAnalysisView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request, *args, **kwargs):
        image_file = request.FILES.get('image')
        method = request.data.get('method', 'ela')

        if not image_file:
            return Response({'error': 'Gambar wajib diunggah.'}, status=400)

        # Save original image temporarily
        ext = os.path.splitext(image_file.name)[1].lower() or '.jpg'
        filename = f"{uuid.uuid4()}{ext}"
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'forensic', 'originals')
        os.makedirs(upload_dir, exist_ok=True)
        filepath = os.path.join(upload_dir, filename)

        with open(filepath, 'wb+') as f:
            for chunk in image_file.chunks():
                f.write(chunk)

        try:
            if method == 'ela':
                result = analyze_ela(filepath)
            elif method == 'noise':
                result = analyze_noise(filepath)
            elif method == 'sharpening':
                result = analyze_sharpening(filepath)
            elif method == 'median_filter':
                result = analyze_median_filter(filepath)
            elif method == 'jpeg_ghost':
                result = analyze_jpeg_ghost(filepath)
            elif method == 'copy_move':
                result = analyze_copy_move(filepath)
            else:
                return Response({'error': f'Metode "{method}" belum tersedia.'}, status=400)

            # Save log
            log = ForensicLog.objects.create(
                image_original=f'forensic/originals/{filename}',
                method=method,
                result_json=result,
                analysis_text=result.get('analysis', ''),
            )

            return Response({
                'log_id': log.id,
                'method': method,
                **result,
            })

        except Exception as e:
            return Response({
                'error': 'Gagal memproses gambar.',
                'details': str(e),
            }, status=500)

    def get(self, request, *args, **kwargs):
        logs = ForensicLog.objects.all()[:50]
        data = [{
            'id': log.id,
            'method': log.method,
            'method_display': log.get_method_display(),
            'image_original': log.image_original.url if log.image_original else None,
            'analysis_text': log.analysis_text,
            'created_at': log.created_at.isoformat(),
        } for log in logs]
        return Response(data)
