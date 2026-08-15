import os
import uuid

from django.db import models


def face_image_path(instance, filename):
    ext = os.path.splitext(filename)[1].lower() or '.jpg'
    return f"face_db/{instance.person_id}/{uuid.uuid4().hex}{ext}"


class Person(models.Model):
    name = models.CharField(max_length=100)
    identifier = models.CharField(max_length=50, unique=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.identifier})"

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