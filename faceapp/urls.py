from django.urls import path
from .views import (FaceCompareView, face_form_view, HistoryView, ModelSettingsView, AboutView,
                     LiveCameraView, save_snapshot, pose_estimation, etle_camera, violation_logs,
                     PersonListView, register_person, identify, delete_person, ForensicAnalysisView)
from .api_views import EtleCameraListView, JogjaCCTVListView

urlpatterns = [
    path('', face_form_view, name='face-form'),
    path('compare/', FaceCompareView.as_view(), name='compare-faces'),
    path('history/', HistoryView.as_view(), name='history'),
    path('model-settings/', ModelSettingsView.as_view(), name='model-settings'),
    path('about/', AboutView.as_view(), name='about'),
    path('live-camera/', LiveCameraView.as_view(), name='live-camera'),
    path("live-camera/save-snapshot/", save_snapshot, name="save_snapshot"),
    path('pose-estimation/', pose_estimation, name='pose_estimation'),
    path('etle-camera/', etle_camera, name='etle_camera'),
    path('etle-camera/cameras/', EtleCameraListView.as_view(), name='etle-camera-cameras'),
    path('etle-camera/cameras/jogja/', JogjaCCTVListView.as_view(), name='jogja-cctv-list'),
    path('violation-logs/', violation_logs, name='violation_logs'),
    path('people/', PersonListView.as_view(), name='people'),
    path('people/register/', register_person, name='register_person'),
    path('people/<int:pk>/delete/', delete_person, name='delete_person'),
    path('identify/', identify, name='identify'),
    path('forensic/ela/', ForensicAnalysisView.as_view(), name='forensic-ela'),
]
