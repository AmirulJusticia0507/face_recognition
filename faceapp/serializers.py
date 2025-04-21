from rest_framework import serializers
from .models import FaceComparisonLog

class FaceComparisonLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = FaceComparisonLog
        fields = '__all__'
