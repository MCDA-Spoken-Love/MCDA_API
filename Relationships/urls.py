from django.urls import path

from . import views

urlpatterns = [
    path('relationship/request/', views.create_relationship_request,
         name='create_relationship_request'),
    path('relationship/respond/<int:pk>/',
         views.respond_relationship_request, name='respond_relationship_request')
]
