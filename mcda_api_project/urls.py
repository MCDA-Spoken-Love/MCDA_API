from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

router = DefaultRouter()


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("apps.Account.urls")),
    path("api/", include("apps.Privacy.urls")),
    path("api/", include("apps.Relationships.urls")),
    path("api/", include("apps.Chat.urls")),
    path("api/", include("apps.Global.urls")),
]
