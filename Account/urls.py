from django.urls import include, path

from . import views

urlpatterns = [
    path('auth/', include('dj_rest_auth.urls')),
    path('auth/registration/', include('dj_rest_auth.registration.urls')),
    path('auth/username/<str:username>/',
         views.get_user_by_username,
         name='get_user_by_username'),
    path('auth/email/<str:email>/',
         views.get_user_by_email,
         name='get_user_by_email'),
]
