import os
import uuid
import base64
import json
from django.utils import timezone
from django.http import JsonResponse
from django.core.files.base import ContentFile
from .models import FaceLog
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from .models import FaceComparisonLog
from .serializers import FaceComparisonLogSerializer
from deepface import DeepFace
from django.views.generic import ListView, TemplateView

class FaceCompareView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request, *args, **kwargs):
        foto_a = request.FILES.get('foto_a')
        foto_b = request.FILES.get('foto_b')
        model_name = request.data.get('model', 'ArcFace')

        if not foto_a or not foto_b:
            return Response({"error": "Kedua foto wajib diunggah."}, status=400)

        # Simpan foto ke media/faces/
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
            # DeepFace face verification
            result = DeepFace.verify(foto_a_path, foto_b_path, model_name=model_name)
            similarity = result.get("distance")
            threshold = result.get("threshold")
            verified = result.get("verified")
            similarity_percent = round((1 - similarity / threshold) * 100, 2)

            # Simpan ke database log
            log = FaceComparisonLog.objects.create(
                foto_a=f'faces/{foto_a_name}',
                foto_b=f'faces/{foto_b_name}',
                model_used=model_name,
                similarity_percent=similarity_percent,
                verified=verified
            )

            serializer = FaceComparisonLogSerializer(log)

            return Response({
                "match": verified,
                "similarity_percent": similarity_percent,
                "model_used": model_name,
                "data": serializer.data
            })

        except Exception as e:
            # Jika DeepFace gagal memproses gambar
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
        FaceLog.objects.create(foto_a=image_file, model_used="Live-Cam", similarity_percent=0,
                               verified=False, created_at=timezone.now(), notes=expression)
        return JsonResponse({"status": "ok"})