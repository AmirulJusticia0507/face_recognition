import os
import uuid
import time
import base64
import tempfile
import requests
from datetime import timedelta

import cv2
import numpy as np
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.core.files.base import ContentFile
from django.conf import settings
from django.db.models import Count, Q
from django.utils.dateparse import parse_date

from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.pagination import PageNumberPagination
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import (
    Person, FaceImage, FaceComparisonLog, FaceLog, PoseLog,
    ViolationLog, ForensicLog, ModelSetting,
)
from .serializers import (
    PersonListSerializer, PersonDetailSerializer, PersonCreateSerializer,
    FaceImageSerializer, FaceComparisonLogSerializer, FaceLogSerializer,
    ViolationLogSerializer, ViolationLogListSerializer, PoseLogSerializer,
    ModelSettingSerializer, ForensicLogSerializer,
)
from . import face_services
from .forensics import (
    analyze_ela, analyze_noise, analyze_sharpening,
    analyze_median_filter, analyze_jpeg_ghost, analyze_copy_move, analyze_metadata,
)
from deepface import DeepFace


class FlexiblePagination(PageNumberPagination):
    page_size_query_param = 'per_page'
    page_size = 20

    def get_page_size(self, request):
        per_page = request.query_params.get(self.page_size_query_param)
        if per_page:
            try:
                return int(per_page)
            except (ValueError, TypeError):
                pass
        return self.page_size


def calculate_pose_score_from_angle(pitch, yaw, roll):
    max_angle = 30
    score = max(0, 100 - (abs(pitch) + abs(yaw) + abs(roll)) / (3 * max_angle) * 100)
    return int(score)


def estimate_pose_and_scores(face_path):
    face_image = cv2.imread(face_path)
    if face_image is None:
        return 50, 50, 50, 50
    gray = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)

    pitch, yaw, roll = 5, 3, 2
    pose_score = calculate_pose_score_from_angle(pitch, yaw, roll)
    brightness = np.mean(gray)
    lighting_score = int(np.clip((brightness / 255) * 100, 0, 100))
    face_detection_confidence = 0.87
    occlusion_score = int(face_detection_confidence * 100)
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    sharpness_score = min(int(laplacian_var / 100 * 100), 100)

    return pose_score, lighting_score, occlusion_score, sharpness_score


AVAILABLE_MODELS = ['ArcFace', 'Facenet', 'VGG-Face', 'OpenFace', 'DeepFace', 'DeepID', 'Dlib']


class AuthLoginView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [JSONParser]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        if not username or not password:
            return Response({'error': 'Username dan password wajib diisi.'}, status=400)

        user = authenticate(username=username, password=password)
        if user is None:
            return Response({'error': 'Username atau password salah.'}, status=401)

        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': {
                'id': user.id,
                'name': user.get_full_name() or user.username,
                'email': user.email,
                'username': user.username,
            }
        })


class AuthRegisterView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [JSONParser]

    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')

        if not username or not password:
            return Response({'error': 'Username dan password wajib diisi.'}, status=400)
        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username sudah digunakan.'}, status=400)

        user = User.objects.create_user(username=username, email=email or '', password=password)
        Token.objects.create(user=user)
        return Response({'success': True, 'message': 'Registrasi berhasil.'}, status=201)


class AuthLogoutView(APIView):
    def post(self, request):
        if hasattr(request.user, 'auth_token'):
            request.user.auth_token.delete()
        return Response({'success': True})


class AuthProfileView(APIView):
    def get(self, request):
        user = request.user
        return Response({
            'id': user.id,
            'name': user.get_full_name() or user.username,
            'email': user.email,
            'username': user.username,
        })

    def put(self, request):
        user = request.user
        user.first_name = request.data.get('name', user.first_name)
        user.email = request.data.get('email', user.email)
        user.save()
        return Response({'success': True})


class AuthChangePasswordView(APIView):
    def post(self, request):
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        if not request.user.check_password(old_password):
            return Response({'error': 'Password lama salah.'}, status=400)
        request.user.set_password(new_password)
        request.user.save()
        return Response({'success': True})


class DashboardStatsView(APIView):
    def get(self, request):
        total_comparisons = FaceComparisonLog.objects.count()
        total_people = Person.objects.count()
        total_violations = ViolationLog.objects.count()
        verified = FaceComparisonLog.objects.filter(verified=True).count()
        accuracy_rate = round((verified / total_comparisons * 100), 1) if total_comparisons > 0 else 0

        return Response({
            'totalComparisons': total_comparisons,
            'totalPeople': total_people,
            'totalViolations': total_violations,
            'accuracyRate': accuracy_rate,
        })


class DashboardRecentActivityView(APIView):
    def get(self, request):
        limit = int(request.query_params.get('limit', 10))
        activities = []

        for log in FaceComparisonLog.objects.all().order_by('-created_at')[:limit]:
            activities.append({
                'id': f'fc-{log.id}',
                'type': 'comparison',
                'description': f'Face comparison: {log.similarity_percent}% similarity ({log.model_used})',
                'timestamp': log.created_at.isoformat(),
            })

        for person in Person.objects.all().order_by('-created_at')[:limit]:
            activities.append({
                'id': f'p-{person.id}',
                'type': 'person',
                'description': f'Person registered: {person.name}',
                'timestamp': person.created_at.isoformat(),
            })

        for log in ViolationLog.objects.all().order_by('-violation_time')[:limit]:
            activities.append({
                'id': f'v-{log.id}',
                'type': 'violation',
                'description': f'Violation: {log.violation_type} ({log.plate_number})',
                'timestamp': log.violation_time.isoformat(),
            })

        activities.sort(key=lambda x: x['timestamp'], reverse=True)
        return Response(activities[:limit])


class DashboardChartView(APIView):
    def get(self, request):
        days = int(request.query_params.get('days', 7))
        today = timezone.now().date()
        labels = []
        data = []

        for i in range(days - 1, -1, -1):
            d = today - timedelta(days=i)
            labels.append(d.strftime('%b %d'))
            count = FaceComparisonLog.objects.filter(
                created_at__date=d
            ).count()
            data.append(count)

        return Response({
            'labels': labels,
            'datasets': [{
                'label': 'Comparisons',
                'data': data,
                'backgroundColor': 'rgba(59, 130, 246, 0.5)',
                'borderColor': 'rgb(59, 130, 246)',
                'borderWidth': 1,
            }]
        })


class PersonListCreateView(APIView):
    pagination_class = FlexiblePagination

    def get(self, request):
        queryset = Person.objects.all()
        search = request.query_params.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(email__icontains=search) |
                Q(identifier__icontains=search)
            )

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)
        serializer = PersonListSerializer(page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = PersonCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        data = serializer.validated_data
        identifier = data.get('identifier') or data.get('email', '') or uuid.uuid4().hex[:8]
        person = Person.objects.create(
            name=data['name'],
            identifier=identifier,
            email=data.get('email', ''),
            phone=data.get('phone', ''),
            address=data.get('address', ''),
            notes=data.get('notes', ''),
        )
        return Response({'id': person.id, 'name': person.name}, status=201)


class PersonDetailView(APIView):
    def get(self, request, pk):
        try:
            person = Person.objects.get(pk=pk)
        except Person.DoesNotExist:
            return Response({'error': 'Person not found'}, status=404)

        serializer = PersonDetailSerializer(person, context={'request': request})
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            person = Person.objects.get(pk=pk)
        except Person.DoesNotExist:
            return Response({'error': 'Person not found'}, status=404)

        person.name = request.data.get('name', person.name)
        person.email = request.data.get('email', person.email)
        person.phone = request.data.get('phone', person.phone)
        person.address = request.data.get('address', person.address)
        person.notes = request.data.get('notes', person.notes)
        person.save()
        return Response({'success': True})

    def delete(self, request, pk):
        try:
            person = Person.objects.get(pk=pk)
        except Person.DoesNotExist:
            return Response({'error': 'Person not found'}, status=404)

        person.delete()
        return Response({'success': True})


class PersonUploadPhotosView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request, pk):
        try:
            person = Person.objects.get(pk=pk)
        except Person.DoesNotExist:
            return Response({'error': 'Person not found'}, status=404)

        photos = request.FILES.getlist('photos')
        if not photos:
            return Response({'error': 'Tidak ada foto yang diunggah.'}, status=400)

        saved = 0
        errors = []
        for photo in photos:
            ok, err = face_services.save_face_image(person, photo)
            if ok:
                saved += 1
            else:
                errors.append(f"{photo.name}: {err}")

        return Response({
            'saved': saved,
            'errors': errors,
            'message': f'{saved} foto berhasil disimpan.',
        })


class PersonPhotosView(APIView):
    def get(self, request, pk):
        try:
            person = Person.objects.get(pk=pk)
        except Person.DoesNotExist:
            return Response({'error': 'Person not found'}, status=404)

        images = person.face_images.all()
        serializer = FaceImageSerializer(images, many=True, context={'request': request})
        return Response(serializer.data)

    def delete(self, request, pk, photo_id):
        try:
            person = Person.objects.get(pk=pk)
        except Person.DoesNotExist:
            return Response({'error': 'Person not found'}, status=404)

        try:
            img = person.face_images.get(pk=photo_id)
            img.delete()
            return Response({'success': True})
        except FaceImage.DoesNotExist:
            return Response({'error': 'Photo not found'}, status=404)


class FaceCompareAPIView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
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

            pose_score, lighting_score, occlusion_score, sharpness_score = estimate_pose_and_scores(foto_a_path)

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


class IdentifyView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        photo = request.FILES.get('photo')
        model_name = request.data.get('model', 'ArcFace')

        if not photo:
            return Response({'error': 'Foto wajib diunggah.'}, status=400)

        tmp = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
        tmp_path = tmp.name
        try:
            for chunk in photo.chunks():
                tmp.write(chunk)
            tmp.close()

            result = face_services.find_best_match(tmp_path, model_name=model_name)
            if result is None:
                return Response({
                    'matched': False,
                    'error': 'Tidak ada kecocokan wajah di database.'
                })

            person = result['person']
            return Response({
                'matched': True,
                'similarity_percent': result['similarity_percent'],
                'model_used': model_name,
                'threshold': result['threshold'],
                'distance': result['distance'],
                'person': {
                    'id': person.id,
                    'name': person.name,
                    'email': person.email,
                    'phone': person.phone,
                    'avatar': person.avatar,
                    'created_at': person.created_at.isoformat(),
                }
            })
        except Exception as e:
            return Response({'error': f'Gagal memproses gambar: {e}'}, status=500)
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def get(self, request):
        return Response({'models': AVAILABLE_MODELS})


class HistoryListView(APIView):
    pagination_class = FlexiblePagination

    def get(self, request):
        queryset = FaceComparisonLog.objects.all()
        search = request.query_params.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(model_used__icontains=search) |
                Q(notes__icontains=search)
            )

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)
        data = [{
            'id': log.id,
            'created_at': log.created_at.isoformat(),
            'model_used': log.model_used,
            'similarity_percent': log.similarity_percent,
            'verified': log.verified,
            'foto_a': log.foto_a.url if log.foto_a else None,
            'foto_b': log.foto_b.url if log.foto_b else None,
        } for log in page]
        return paginator.get_paginated_response(data)


class HistoryDetailView(APIView):
    def get(self, request, pk):
        try:
            log = FaceComparisonLog.objects.get(pk=pk)
        except FaceComparisonLog.DoesNotExist:
            return Response({'error': 'Not found'}, status=404)

        return Response({
            'id': log.id,
            'created_at': log.created_at.isoformat(),
            'model_used': log.model_used,
            'similarity_percent': log.similarity_percent,
            'verified': log.verified,
            'foto_a': log.foto_a.url if log.foto_a else None,
            'foto_b': log.foto_b.url if log.foto_b else None,
        })

    def delete(self, request, pk):
        try:
            log = FaceComparisonLog.objects.get(pk=pk)
            log.delete()
            return Response({'success': True})
        except FaceComparisonLog.DoesNotExist:
            return Response({'error': 'Not found'}, status=404)


class HistoryClearView(APIView):
    def delete(self, request):
        FaceComparisonLog.objects.all().delete()
        return Response({'success': True})


class ModelSettingsView(APIView):
    def get(self, request):
        settings_obj = ModelSetting.get_solo()
        serializer = ModelSettingSerializer(settings_obj)
        return Response(serializer.data)

    def put(self, request):
        settings_obj = ModelSetting.get_solo()
        serializer = ModelSettingSerializer(settings_obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True})
        return Response(serializer.errors, status=400)


class ModelSettingsAvailableView(APIView):
    def get(self, request):
        return Response(AVAILABLE_MODELS)


class ModelSettingsTestView(APIView):
    parser_classes = [JSONParser]

    def post(self, request):
        model_name = request.data.get('model', 'ArcFace')

        dummy = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
        tmp_path = os.path.join(settings.MEDIA_ROOT, 'tmp_test.jpg')
        os.makedirs(os.path.dirname(tmp_path), exist_ok=True)
        cv2.imwrite(tmp_path, dummy)

        try:
            start = time.time()
            DeepFace.represent(img_path=tmp_path, model_name=model_name, enforce_detection=False)
            elapsed = round((time.time() - start) * 1000, 2)

            return Response({
                'avg_time': elapsed,
                'memory_usage': 0,
                'model': model_name,
            })
        except Exception as e:
            return Response({
                'error': f'Test gagal: {str(e)}',
                'avg_time': 0,
                'memory_usage': 0,
            }, status=500)
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)


class LiveCameraSnapshotView(APIView):
    parser_classes = [JSONParser]

    def post(self, request):
        image_data = request.data.get('image_base64', '')
        expression = request.data.get('detected_expression', '')

        if not image_data:
            return Response({'error': 'image_base64 wajib diisi.'}, status=400)

        try:
            if ',' in image_data:
                image_data = image_data.split(',')[1]
            image_file = ContentFile(base64.b64decode(image_data), name="snapshot.jpg")

            log = FaceLog.objects.create(
                foto_a=image_file,
                model_used="Live-Cam",
                similarity_percent=0,
                verified=False,
                notes=expression,
            )

            return Response({
                'success': True,
                'id': log.id,
                'message': 'Snapshot tersimpan.',
            })
        except Exception as e:
            return Response({'error': f'Gagal menyimpan snapshot: {e}'}, status=500)


class LiveCameraSnapshotsView(APIView):
    pagination_class = FlexiblePagination

    def get(self, request):
        limit = int(request.query_params.get('limit', 20))
        logs = FaceLog.objects.all().order_by('-created_at')[:limit]
        data = [{
            'id': log.id,
            'foto_a': log.foto_a.url if log.foto_a else None,
            'created_at': log.created_at.isoformat(),
            'notes': log.notes,
        } for log in logs]
        return Response({'results': data})

    def delete(self, request, pk):
        try:
            log = FaceLog.objects.get(pk=pk)
            log.delete()
            return Response({'success': True})
        except FaceLog.DoesNotExist:
            return Response({'error': 'Not found'}, status=404)


class PoseEstimationView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        photo = request.FILES.get('photo')
        if not photo:
            return Response({'error': 'Foto wajib diunggah.'}, status=400)

        tmp = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
        tmp_path = tmp.name
        try:
            for chunk in photo.chunks():
                tmp.write(chunk)
            tmp.close()

            pose_score, lighting_score, occlusion_score, sharpness_score = estimate_pose_and_scores(tmp_path)
            overall = round((pose_score + lighting_score + occlusion_score + sharpness_score) / 4)

            return Response({
                'overall_score': overall,
                'pose_score': pose_score,
                'lighting_score': lighting_score,
                'occlusion_score': occlusion_score,
                'sharpness_score': sharpness_score,
                'angles': {'pitch': 5, 'yaw': 3, 'roll': 2},
            })
        except Exception as e:
            return Response({'error': f'Gagal memproses: {e}'}, status=500)
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def get(self, request):
        logs = PoseLog.objects.all().order_by('-timestamp')[:50]
        data = PoseLogSerializer(logs, many=True).data
        return Response({'results': data})


ETLE_CAMERAS = [
    {'id': 'cam-001', 'name': 'Simpang APMD (PTZ)', 'lat': -7.791971853164589, 'lng': 110.39164423942567, 'source': 'jogjakota', 'stream': 'https://cctvjss.jogjakota.go.id/atcs/ATCS_apmd.stream/playlist.m3u8', 'status': 'online'},
    {'id': 'cam-002', 'name': 'Simpang Gondomanan (PTZ)', 'lat': -7.801683039634787, 'lng': 110.36917244417295, 'source': 'jogjakota', 'stream': 'https://cctvjss.jogjakota.go.id/atcs/ATCS_gondomanan.stream/playlist.m3u8', 'status': 'online'},
    {'id': 'cam-003', 'name': 'Simpang Jokteng Kulon (PTZ)', 'lat': -7.81294, 'lng': 110.35594, 'source': 'jogjakota', 'stream': 'https://cctvjss.jogjakota.go.id/atcs/ATCS_joktengkulon.stream/playlist.m3u8', 'status': 'online'},
    {'id': 'cam-004', 'name': 'Simpang Jokteng Wetan', 'lat': -7.814380894891082, 'lng': 110.36806762218477, 'source': 'jogjakota', 'stream': 'https://cctvjss.jogjakota.go.id/atcs/ATCS_joktengwetan.stream/playlist.m3u8', 'status': 'online'},
    {'id': 'cam-005', 'name': 'Simpang KM Nol (PTZ)', 'lat': -7.8010758219105565, 'lng': 110.36475215767108, 'source': 'jogjakota', 'stream': 'https://cctvjss.jogjakota.go.id/atcs/ATCS_kmnol.stream/playlist.m3u8', 'status': 'online'},
    {'id': 'cam-006', 'name': 'Simpang Permata (PTZ)', 'lat': -7.8015437731163875, 'lng': 110.37307262420656, 'source': 'jogjakota', 'stream': 'https://cctvjss.jogjakota.go.id/atcs/ATCS_permata.stream/playlist.m3u8', 'status': 'online'},
    {'id': 'cam-007', 'name': 'Simpang PKU Muh. (PTZ)', 'lat': -7.801283, 'lng': 110.362061, 'source': 'jogjakota', 'stream': 'https://cctvjss.jogjakota.go.id/atcs/ATCS_pkumuh.stream/playlist.m3u8', 'status': 'online'},
    {'id': 'cam-008', 'name': 'Simpang Sentul (PTZ)', 'lat': -7.801442745827733, 'lng': 110.3779435343926, 'source': 'jogjakota', 'stream': 'https://cctvjss.jogjakota.go.id/atcs/ATCS_sentul.stream/playlist.m3u8', 'status': 'online'},
]


class EtleCameraListView(APIView):
    def get(self, request):
        return Response(ETLE_CAMERAS)

class JogjaCCTVListView(APIView):
    def get(self, request):
        try:
            resp = requests.get(
                'https://cctv.jogjakota.go.id/home/getdata',
                timeout=10,
                headers={'Accept': 'application/json'}
            )
            if resp.status_code == 200:
                data = resp.json()
                cameras = []
                for cam in data:
                    link = cam.get('cctv_link', '')
                    status = cam.get('cctv_status', '0')
                    cameras.append({
                        'id': cam.get('cctv_id', ''),
                        'name': cam.get('cctv_title', ''),
                        'lat': float(cam.get('cctv_latitude', 0)) if cam.get('cctv_latitude') else None,
                        'lng': float(cam.get('cctv_longitude', 0)) if cam.get('cctv_longitude') else None,
                        'source': 'jogjakota',
                        'stream': link.replace('https://cctvjss.jogjakota.go.id/', 'https://cctv.jogjakota.go.id/').replace('/playlist.m3u8', '') if link else '',
                        'status': 'online' if status == '0' else 'offline',
                    })
                return Response(cameras[:20])
except Exception as e:
                    pass
        return Response(ETLE_CAMERAS)


class CameraListCreateView(APIView):
    parser_classes = [JSONParser, MultiPartParser]

    def get(self, request):
        cameras = Camera.objects.all().order_by('name')
        serializer = CameraSerializer(cameras, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CameraSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CameraRetrieveUpdateDestroyView(APIView):
    parser_classes = [JSONParser, MultiPartParser]

    def get_object(self, pk):
        try:
            return Camera.objects.get(pk=pk)
        except Camera.DoesNotExist:
            return Response({'error': 'Camera not found'}, status=status.HTTP_404_NOT_FOUND)

    def get(self, request, pk):
        camera = self.get_object(pk)
        serializer = CameraSerializer(camera)
        return Response(serializer.data)

    def put(self, request, pk):
        camera = self.get_object(pk)
        serializer = CameraSerializer(camera, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        camera = self.get_object(pk)
        camera.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class EtleCameraDetectView(APIView):
    parser_classes = [JSONParser, MultiPartParser]

    def post(self, request):
        image = request.data.get('image')
        camera = request.data.get('camera', '')
        stream_url = request.data.get('stream_url', '')
        mode = request.data.get('mode', 'local')

        frame_path = None

        if mode == 'proxy' and stream_url:
            try:
                cap = cv2.VideoCapture(stream_url)
                if not cap.isOpened():
                    return Response({'error': f'Gagal membuka stream: {stream_url}'}, status=400)
                ret, frame = cap.read()
                cap.release()
                if not ret or frame is None:
                    return Response({'error': 'Gagal membaca frame dari stream'}, status=400)
                tmp = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
                frame_path = tmp.name
                tmp.close()
                cv2.imwrite(frame_path, frame)
                image_file = frame_path
            except Exception as e:
                return Response({'error': f'Proxy capture error: {e}'}, status=500)
        elif image:
            image_data = image.split(',')[-1] if ',' in image else image
            tmp = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
            frame_path = tmp.name
            tmp.close()
            with open(frame_path, 'wb') as f:
                f.write(base64.b64decode(image_data))
            image_file = frame_path
        else:
            return Response({'error': 'Image atau stream_url wajib diisi.'}, status=400)

        violations = []
        try:
            img = cv2.imread(image_file)
            if img is not None:
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                height, width = gray.shape

                bright = cv2.mean(gray)[0]
                if bright > 200:
                    violations.append({
                        'type': 'glare',
                        'description': 'Cahaya berlebihan / silau terdeteksi',
                        'time': timezone.now().isoformat(),
                        'camera': camera,
                    })

                edges = cv2.Canny(gray, 100, 200)
                edge_ratio = cv2.countNonZero(edges) / (height * width)
                if edge_ratio > 0.15:
                    violations.append({
                        'type': 'scene_change',
                        'description': 'Perubahan scene signifikan terdeteksi',
                        'time': timezone.now().isoformat(),
                        'camera': camera,
                    })

                face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                faces = face_cascade.detectMultiScale(gray, 1.3, 5)
                if len(faces) > 5:
                    violations.append({
                        'type': 'crowd',
                        'description': f'Kerumunan terdeteksi ({len(faces)} wajah)',
                        'time': timezone.now().isoformat(),
                        'camera': camera,
                    })

                blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
                if blur_score < 50:
                    violations.append({
                        'type': 'blur',
                        'description': 'Gambar buram / tidak fokus',
                        'time': timezone.now().isoformat(),
                        'camera': camera,
                    })

                if not violations:
                    violations.append({
                        'type': 'normal',
                        'description': 'Tidak ada pelanggaran terdeteksi',
                        'time': timezone.now().isoformat(),
                        'camera': camera,
                    })

                ViolationLog.objects.create(
                    violation_type=violations[0]['type'],
                    description=violations[0]['description'],
                    camera_id=camera,
                )

        except Exception as e:
            violations.append({
                'type': 'error',
                'description': f'Error analisis: {e}',
                'time': timezone.now().isoformat(),
                'camera': camera,
            })
        finally:
            if frame_path and os.path.exists(frame_path):
                os.unlink(frame_path)

        return Response({'violations': violations})


class ViolationLogsListView(APIView):
    pagination_class = FlexiblePagination

    def get(self, request):
        queryset = ViolationLog.objects.all()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)
        serializer = ViolationLogListSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class ViolationLogsDetailView(APIView):
    def get(self, request, pk):
        try:
            log = ViolationLog.objects.get(pk=pk)
        except ViolationLog.DoesNotExist:
            return Response({'error': 'Not found'}, status=404)

        serializer = ViolationLogSerializer(log)
        return Response(serializer.data)

    def delete(self, request, pk):
        try:
            log = ViolationLog.objects.get(pk=pk)
            log.delete()
            return Response({'success': True})
        except ViolationLog.DoesNotExist:
            return Response({'error': 'Not found'}, status=404)


class ViolationLogsStatsView(APIView):
    def get(self, request):
        now = timezone.now()
        today = now.date()
        week_start = today - timedelta(days=today.weekday())

        return Response({
            'total': ViolationLog.objects.count(),
            'today': ViolationLog.objects.filter(violation_time__date=today).count(),
            'thisWeek': ViolationLog.objects.filter(violation_time__date__gte=week_start).count(),
        })


class ViolationLogsExportCSVView(APIView):
    def get(self, request):
        import csv
        import io
        from django.http import HttpResponse

        queryset = ViolationLog.objects.all().order_by('-violation_time')
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="violation_logs.csv"'
        writer = csv.writer(response)
        writer.writerow(['ID', 'Plat Nomor', 'Waktu', 'Jenis', 'Kamera', 'Deskripsi', 'Status', 'Grafi'])
        for log in queryset:
            writer.writerow([
                log.id,
                log.plate_number,
                log.violation_time.strftime('%Y-%m-%d %H:%M:%S') if log.violation_time else '',
                log.violation_type,
                log.camera_name or '',
                log.description or '',
                log.status,
                log.fine_amount or '',
            ])
        return response


class ForensicAnalysisAPIView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        image_file = request.FILES.get('image')
        method = request.data.get('method', 'ela')

        if not image_file:
            return Response({'error': 'Gambar wajib diunggah.'}, status=400)

        ext = os.path.splitext(image_file.name)[1].lower() or '.jpg'
        filename = f"{uuid.uuid4()}{ext}"
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'forensic', 'originals')
        os.makedirs(upload_dir, exist_ok=True)
        filepath = os.path.join(upload_dir, filename)

        with open(filepath, 'wb+') as f:
            for chunk in image_file.chunks():
                f.write(chunk)

        try:
            method_map = {
                'ela': analyze_ela,
                'noise': analyze_noise,
                'sharpening': analyze_sharpening,
                'median_filter': analyze_median_filter,
                'jpeg_ghost': analyze_jpeg_ghost,
                'copy_move': analyze_copy_move,
                'metadata': analyze_metadata,
            }
            if method not in method_map:
                return Response({'error': f'Metode "{method}" belum tersedia.'}, status=400)

            result = method_map[method](filepath)

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

    def get(self, request):
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
