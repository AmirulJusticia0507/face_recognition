import os
import uuid
import base64
import json
import cv2
import numpy as np
from django.utils import timezone
from django.http import JsonResponse
from django.core.files.base import ContentFile
from django.conf import settings
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from django.views.generic import ListView, TemplateView
from .models import FaceLog, FaceComparisonLog, ViolationLog
from .serializers import FaceComparisonLogSerializer
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
