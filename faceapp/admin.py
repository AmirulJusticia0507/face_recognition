from django.contrib import admin

from .models import FaceComparisonLog, FaceLog, PoseLog, ViolationLog, Person, FaceImage


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
