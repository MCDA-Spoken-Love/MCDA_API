from django.urls import path

from . import views

urlpatterns = [
    path('relationship/request/', views.CreateRelationshipRequestView.as_view(),
         name='create_relationship_request'),
    path('relationship/respond/<int:pk>/',
         views.RespondRelationshipRequestView.as_view(), name='respond_relationship_request'),
    path('relationship/', views.ManageRelationshipsView.as_view(),
         name='manage_relationship')
]
