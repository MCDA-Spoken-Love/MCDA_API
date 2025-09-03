from django.urls import path

from .views import PrivacySettingsView, ToggleLastSeenView, ToggleStatusVisibilityView

urlpatterns = [
    path('privacy/', PrivacySettingsView.as_view(),
         name='get_privacy_settings'),
    path('toggle-status-visibility/', ToggleStatusVisibilityView.as_view(),
         name='toggle_status_visibility'),
    path('toggle-last-seen/', ToggleLastSeenView.as_view(), name='toggle_last_seen'),
]
