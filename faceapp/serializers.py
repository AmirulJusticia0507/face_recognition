from rest_framework import serializers
from .models import (
    FaceComparisonLog, ForensicLog, Person, FaceImage,
    FaceLog, ViolationLog, PoseLog, ModelSetting,
)


class FaceComparisonLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = FaceComparisonLog
        fields = '__all__'


class ForensicLogSerializer(serializers.ModelSerializer):
    method_display = serializers.CharField(source='get_method_display', read_only=True)

    class Meta:
        model = ForensicLog
        fields = '__all__'
        read_only_fields = ['created_at']


class FaceImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = FaceImage
        fields = ['id', 'image', 'uploaded_at']


class PersonListSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()
    photo_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Person
        fields = ['id', 'name', 'email', 'phone', 'avatar', 'photo_count', 'created_at']

    def get_avatar(self, obj):
        img = obj.face_images.first()
        if img and img.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(img.image.url)
            return img.image.url
        return None


class PersonDetailSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()
    photo_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Person
        fields = ['id', 'name', 'identifier', 'email', 'phone', 'address', 'notes', 'avatar', 'photo_count', 'created_at']

    def get_avatar(self, obj):
        img = obj.face_images.first()
        if img and img.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(img.image.url)
            return img.image.url
        return None


class PersonCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ['id', 'name', 'identifier', 'email', 'phone', 'address', 'notes']


class FaceLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = FaceLog
        fields = '__all__'


class ViolationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ViolationLog
        fields = '__all__'


class ViolationLogListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ViolationLog
        fields = ['id', 'violation_time', 'violation_type', 'plate_number', 'location', 'status', 'fine_amount', 'vehicle_image', 'driver_image']


class PoseLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = PoseLog
        fields = '__all__'


class ModelSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelSetting
        fields = ['default_model', 'similarity_threshold', 'detection_backend', 'enforce_detection', 'align']
