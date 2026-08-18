from rest_framework import serializers
from .models import FaceComparisonLog, ForensicLog


class FaceComparisonLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = FaceComparisonLog
        fields = '__all__'


class ForensicLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ForensicLog
        fields = '__all__'
        read_only_fields = ['created_at']
