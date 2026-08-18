from django.urls import path
from . import api_views as v

urlpatterns = [
    path('auth/login/', v.AuthLoginView.as_view(), name='api-auth-login'),
    path('auth/register/', v.AuthRegisterView.as_view(), name='api-auth-register'),
    path('auth/logout/', v.AuthLogoutView.as_view(), name='api-auth-logout'),
    path('auth/profile/', v.AuthProfileView.as_view(), name='api-auth-profile'),
    path('auth/change-password/', v.AuthChangePasswordView.as_view(), name='api-auth-change-password'),

    path('dashboard/stats/', v.DashboardStatsView.as_view(), name='api-dashboard-stats'),
    path('dashboard/recent-activity/', v.DashboardRecentActivityView.as_view(), name='api-dashboard-recent'),
    path('dashboard/charts/', v.DashboardChartView.as_view(), name='api-dashboard-charts'),

    path('people/', v.PersonListCreateView.as_view(), name='api-people-list'),
    path('people/<int:pk>/', v.PersonDetailView.as_view(), name='api-people-detail'),
    path('people/<int:pk>/upload-photos/', v.PersonUploadPhotosView.as_view(), name='api-people-upload'),
    path('people/<int:pk>/photos/', v.PersonPhotosView.as_view(), name='api-people-photos'),
    path('people/<int:pk>/photos/<int:photo_id>/', v.PersonPhotosView.as_view(), name='api-people-photo-delete'),

    path('face-compare/', v.FaceCompareAPIView.as_view(), name='api-face-compare'),
    path('face-comparison/history/', v.HistoryListView.as_view(), name='api-face-comparison-history'),
    path('face-comparison/<int:pk>/', v.HistoryDetailView.as_view(), name='api-face-comparison-detail'),

    path('identify/', v.IdentifyView.as_view(), name='api-identify'),
    path('identify/models/', v.IdentifyView.as_view(), name='api-identify-models'),

    path('history/', v.HistoryListView.as_view(), name='api-history-list'),
    path('history/clear/', v.HistoryClearView.as_view(), name='api-history-clear'),
    path('history/<int:pk>/', v.HistoryDetailView.as_view(), name='api-history-detail'),

    path('model-settings/', v.ModelSettingsView.as_view(), name='api-model-settings'),
    path('model-settings/available/', v.ModelSettingsAvailableView.as_view(), name='api-model-settings-available'),
    path('model-settings/test/', v.ModelSettingsTestView.as_view(), name='api-model-settings-test'),

    path('live-camera/snapshot/', v.LiveCameraSnapshotView.as_view(), name='api-live-camera-snapshot'),
    path('live-camera/snapshots/', v.LiveCameraSnapshotsView.as_view(), name='api-live-camera-snapshots'),
    path('live-camera/snapshots/<int:pk>/', v.LiveCameraSnapshotsView.as_view(), name='api-live-camera-snapshot-delete'),

    path('pose-estimation/', v.PoseEstimationView.as_view(), name='api-pose-estimation'),
    path('pose-estimation/history/', v.PoseEstimationView.as_view(), name='api-pose-estimation-history'),

    path('etle-camera/cameras/', v.EtleCameraListView.as_view(), name='api-etle-cameras'),
    path('etle-camera/detect/', v.EtleCameraDetectView.as_view(), name='api-etle-detect'),

    path('violation-logs/', v.ViolationLogsListView.as_view(), name='api-violation-logs'),
    path('violation-logs/stats/', v.ViolationLogsStatsView.as_view(), name='api-violation-logs-stats'),
    path('violation-logs/<int:pk>/', v.ViolationLogsDetailView.as_view(), name='api-violation-log-detail'),

    path('forensic/ela/', v.ForensicAnalysisAPIView.as_view(), name='api-forensic-ela'),
]
