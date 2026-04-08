from django.urls import path

from apps.Global.views import PresignImageView

urlpatterns = [
    path("global/image/presign/", PresignImageView.as_view(), name="presign_image"),
]
