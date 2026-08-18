import os
import uuid

from django.db import models


def face_image_path(instance, filename):
    ext = os.path.splitext(filename)[1].lower() or '.jpg'
    return f"face_db/{instance.person_id}/{uuid.uuid4().hex}{ext}"


class Person(models.Model):
    name = models.CharField(max_length=100)
    identifier = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.identifier})"

    @property
    def avatar(self):
        img = self.face_images.first()
        if img and img.image:
            return img.image.url
        return None

    @property
    def photo_count(self):
        return self.face_images.count()

    def delete(self, *args, **kwargs):
        for face_image in self.face_images.all():
            face_image.image.delete(save=False)
        super().delete(*args, **kwargs)


class FaceImage(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='face_images')
    image = models.ImageField(upload_to=face_image_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.person.name} - {self.image.name}"

    def delete(self, *args, **kwargs):
        self.image.delete(save=False)
        super().delete(*args, **kwargs)


class FaceComparisonLog(models.Model):
    foto_a = models.ImageField(upload_to='faces/')
    foto_b = models.ImageField(upload_to='faces/')
    model_used = models.CharField(max_length=50)
    similarity_percent = models.FloatField()
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.model_used} - {self.similarity_percent}% match"

class FaceLog(models.Model):
    foto_a = models.ImageField(upload_to='snapshots/')
    model_used = models.CharField(max_length=50)
    similarity_percent = models.FloatField(default=0)
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Snapshot {self.id} - {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"

class PoseLog(models.Model):
    pose = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='pose_snapshots/', null=True, blank=True)

class ViolationLog(models.Model):
    plate_number = models.CharField(max_length=20)
    vehicle_image = models.ImageField(upload_to='violations/')
    driver_image = models.ImageField(upload_to='violations/', null=True, blank=True)
    violation_type = models.CharField(max_length=50)
    violation_time = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    fine_amount = models.FloatField(null=True, blank=True)
    status = models.CharField(max_length=20, default='Pending')

    def __str__(self):
        return f"Violation: {self.plate_number} - {self.violation_type} at {self.violation_time.strftime('%Y-%m-%d %H:%M:%S')}"


class ForensicLog(models.Model):
    METHOD_CHOICES = [
        ('ela', 'Error Level Analysis'),
        ('noise', 'Noise Analysis'),
        ('sharpening', 'Sharpening Detection'),
        ('median_filter', 'Median Filter Detection'),
        ('copy_move', 'Copy-Move Detection'),
        ('jpeg_ghost', 'JPEG Ghost Detection'),
        ('metadata', 'Metadata Forensics'),
    ]

    image_original = models.ImageField(upload_to='forensic/originals/')
    image_result = models.ImageField(upload_to='forensic/results/', blank=True, null=True)
    method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    result_json = models.JSONField(default=dict)
    analysis_text = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_method_display()} - {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"

    def delete(self, *args, **kwargs):
        self.image_original.delete(save=False)
        if self.image_result:
            self.image_result.delete(save=False)
        super().delete(*args, **kwargs)


class ModelSetting(models.Model):
    default_model = models.CharField(max_length=50, default='ArcFace')
    similarity_threshold = models.FloatField(default=0.4)
    detection_backend = models.CharField(max_length=50, default='opencv')
    enforce_detection = models.BooleanField(default=True)
    align = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Model Settings'

    def __str__(self):
        return f"Model Settings ({self.default_model})"

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class Camera(models.Model):
    SOURCE_CHOICES = [
        ('jogjakota', 'Jogja Kota (cctv.jogjakota.go.id)'),
        ('sleman', 'Sleman (24jam.slemankab.go.id)'),
        ('bantul', 'Bantul (bantulkab.go.id)'),
        ('ai_cctv', 'AI CCTV External'),
    ]
    STATUS_CHOICES = [
        ('online', 'Online'),
        ('offline', 'Offline'),
        ('maintenance', 'Maintenance'),
    ]

    name = models.CharField(max_length=100)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    stream_url = models.URLField(blank=True, null=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='online')
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_source_display})"