from django.urls import re_path

from .consumers import RelationshipConsumer

relationship_ws_urlpatterns = [
    re_path(r"ws/relationship-requests/$",
            RelationshipConsumer.as_asgi()),
]
