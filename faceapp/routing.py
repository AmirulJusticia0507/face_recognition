from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path('ws/detections/', consumers.DetectionNotificationConsumer.as_asgi()),
]
