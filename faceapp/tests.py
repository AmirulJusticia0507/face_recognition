from io import StringIO

import numpy as np
from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from .camera_scanner import detect_faces_in_frame
from .management.commands.run_camera_scans import Command as ScanCommand
from .models import Camera, CameraScanLog


@override_settings(
    SECURE_SSL_REDIRECT=False,
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    FRONTEND_URL='http://localhost:5173',
)
class AuthAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_signup_login_by_email_and_password_reset(self):
        register_response = self.client.post(reverse('api-auth-register'), {
            'username': 'authuser',
            'email': 'auth@example.com',
            'password': 'StrongPassword123!',
        }, format='json')
        self.assertEqual(register_response.status_code, 201)

        login_response = self.client.post(reverse('api-auth-login'), {
            'username': 'auth@example.com',
            'password': 'StrongPassword123!',
        }, format='json')
        self.assertEqual(login_response.status_code, 200)

        forgot_response = self.client.post(reverse('api-auth-forgot-password'), {
            'email': 'auth@example.com',
        }, format='json')
        self.assertEqual(forgot_response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)

        user = User.objects.get(username='authuser')
        from django.contrib.auth.tokens import default_token_generator
        from django.utils.encoding import force_bytes
        from django.utils.http import urlsafe_base64_encode
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        reset_response = self.client.post(reverse('api-auth-reset-password'), {
            'uid': uid,
            'token': token,
            'password': 'NewStrongPassword123!',
            'confirm_password': 'NewStrongPassword123!',
        }, format='json')
        self.assertEqual(reset_response.status_code, 200)

        old_login = self.client.post(reverse('api-auth-login'), {
            'username': 'authuser',
            'password': 'StrongPassword123!',
        }, format='json')
        new_login = self.client.post(reverse('api-auth-login'), {
            'username': 'authuser',
            'password': 'NewStrongPassword123!',
        }, format='json')
        self.assertEqual(old_login.status_code, 401)
        self.assertEqual(new_login.status_code, 200)


@override_settings(SECURE_SSL_REDIRECT=False)


@override_settings(SECURE_SSL_REDIRECT=False)
class CameraModelTests(TestCase):
    def test_camera_str(self):
        cam = Camera.objects.create(name='Gate 1', source='jogjakota', stream_url='https://example.com/x.m3u8')
        self.assertIn('Gate 1', str(cam))


class CameraScanLogTests(TestCase):
    def test_error_log_created_when_no_stream(self):
        cam = Camera.objects.create(name='No Stream', source='custom')
        log = CameraScanLog.objects.create(
            camera=cam,
            camera_name=cam.name,
            image='camera_scans/placeholder.jpg',
            model_used='haar',
        )
        self.assertEqual(log.face_detected, False)


class FaceDetectionTests(TestCase):
    def test_detect_faces_in_blank_frame(self):
        img = np.full((480, 640, 3), 255, dtype=np.uint8)
        result = detect_faces_in_frame(img, identify=False)
        self.assertEqual(result['face_count'], 0)
        self.assertFalse(result['face_detected'])


@override_settings(SECURE_SSL_REDIRECT=False)
class CameraScanAPITests(TestCase):
    def setUp(self):
        from django.contrib.auth.models import User
        self.auth_user = User.objects.create_user(username='admin', password='pass')
        self.token = Token.objects.create(user=self.auth_user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

    def test_scan_now_without_stream(self):
        cam = Camera.objects.create(name='Empty', source='custom')
        url = reverse('api-cameras-scan', kwargs={'pk': cam.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        results = response.json()['results'][0]
        self.assertEqual(results['status'], 'error')

    def test_scan_status_endpoint(self):
        url = reverse('api-camera-scans-status')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class RunCameraScansCommandTests(TestCase):
    def setUp(self):
        from django.contrib.auth.models import User
        self.auth_user = User.objects.create_user(username='admin', password='pass')

    def test_command_runs_for_no_active_cameras(self):
        cmd = ScanCommand()
        out = StringIO()
        cmd.stdout = out
        cmd.handle(once=True)
        self.assertGreater(len(out.getvalue()), 0)
