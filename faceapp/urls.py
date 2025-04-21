from django.urls import path
from .views import FaceCompareView, face_form_view,HistoryView,ModelSettingsView,AboutView,LiveCameraView, save_snapshot

urlpatterns = [
    path('', face_form_view, name='face-form'),
    path('compare/', FaceCompareView.as_view(), name='compare-faces'),
    path('history/', HistoryView.as_view(), name='history'),
    path('model-settings/', ModelSettingsView.as_view(), name='model-settings'),
    path('about/', AboutView.as_view(), name='about'),
    path('live-camera/', LiveCameraView.as_view(), name='live-camera'),
    path("live-camera/save-snapshot/", save_snapshot, name="save_snapshot"),
]
