from django.contrib import admin

from .models import (
    FaceComparisonLog, FaceLog, PoseLog, ViolationLog, Person, FaceImage,
    ForensicLog, Camera, CameraScanLog,
)


@admin.register(Camera)
class CameraAdmin(admin.ModelAdmin):
    list_display = ['name', 'source', 'status', 'building', 'room', 'floor', 'auto_scan', 'scan_interval_seconds', 'last_scanned_at']
    list_filter = ['status', 'source', 'auto_scan']
    search_fields = ['name', 'stream_url', 'building', 'room']


@admin.register(CameraScanLog)
class CameraScanLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'camera_name', 'building', 'room', 'face_detected', 'face_count', 'model_used', 'created_at']
    list_filter = ['face_detected', 'model_used', 'detection_method', 'created_at']
    search_fields = ['camera_name', 'building', 'room']
    date_hierarchy = 'created_at'


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ['name', 'identifier', 'created_at']
    search_fields = ['name', 'identifier']


@admin.register(FaceImage)
class FaceImageAdmin(admin.ModelAdmin):
    list_display = ['person', 'uploaded_at']
    search_fields = ['person__name', 'person__identifier']


@admin.register(FaceComparisonLog)
class FaceComparisonLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'model_used', 'similarity_percent', 'verified', 'created_at']
    list_filter = ['model_used', 'verified']


@admin.register(FaceLog)
class FaceLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'model_used', 'created_at']


@admin.register(PoseLog)
class PoseLogAdmin(admin.ModelAdmin):
    list_display = ['pose', 'timestamp']


@admin.register(ViolationLog)
class ViolationLogAdmin(admin.ModelAdmin):
    list_display = ['plate_number', 'violation_type', 'violation_time', 'status']
    list_filter = ['status', 'violation_type']
    search_fields = ['plate_number']


@admin.register(ForensicLog)
class ForensicLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'method', 'created_at']
    list_filter = ['method']
    search_fields = ['method']
