
from django.urls import path

from . import views

urlpatterns = [
    path('privacy/', views.get_privacy_settings,
         name='get_privacy_settings'),
    path('privacy/toggle/status/', views.toggle_status_visibility,
         name='toggle_status_visibility'),
    path('privacy/toggle/last_seen/',
         views.toggle_last_seen, name='toggle_last_seen')
]
