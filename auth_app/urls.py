from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from .views import SignUpView, my_view  # Import your views here

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', LoginView.as_view(template_name='accounts/login.html'),
         name='login'),  # Using Django's built-in LoginView
    # Using Django's built-in LogoutView
    path('logout/', LogoutView.as_view(), name='logout'),
    # Adjust this to your view
    path('image/', my_view, name='image'),
]
