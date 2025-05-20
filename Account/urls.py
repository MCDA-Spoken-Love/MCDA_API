from django.urls import include, path

from . import views

urlpatterns = [
    path('auth/', include('dj_rest_auth.urls')),
    path('auth/registration/', include('dj_rest_auth.registration.urls')),
    path('user/search/', views.get_user_by_filter, name='get_user_by_username'),
    path('user/relationship/', views.manager_user_relationshop,
         name='manager_user_relationship'),
]
