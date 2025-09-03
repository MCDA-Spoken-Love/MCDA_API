from django.urls import path

from .views import PrivacySettingsView, ToggleLastSeenView, ToggleStatusVisibilityView

urlpatterns = [
    path('privacy-settings/', PrivacySettingsView.as_view()),
    path('toggle-status-visibility/', ToggleStatusVisibilityView.as_view()),
    path('toggle-last-seen/', ToggleLastSeenView.as_view()),
]
