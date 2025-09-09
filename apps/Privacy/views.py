from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.Privacy.models import UserPrivacy
from apps.Privacy.serializer import UserPrivacySerializer


class PrivacySettingsView(APIView):
    def get(self, request):
        try:
            user = request.user
            privacy_settings, created = UserPrivacy.objects.get_or_create(
                user=user)
            serializer = UserPrivacySerializer(privacy_settings)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": "Error in getting user status visibility", "full_error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ToggleStatusVisibilityView(APIView):
    def put(self, request):
        try:
            user = request.user
            privacy_settings, created = UserPrivacy.objects.get_or_create(
                user=user)
            privacy_settings.allow_status_visibility = not privacy_settings.allow_status_visibility
            privacy_settings.save()
            serializer = UserPrivacySerializer(privacy_settings)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": "Error in managing user status visibility", "full_error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ToggleOnlineStatusVisibilityView(APIView):
    def put(self, request):
        try:
            user = request.user
            privacy_settings, created = UserPrivacy.objects.get_or_create(
                user=user)
            privacy_settings.allow_online_status_visibility = not privacy_settings.allow_online_status_visibility
            privacy_settings.save()
            serializer = UserPrivacySerializer(privacy_settings)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": "Error in managing user online status visibility", "full_error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ToggleLastSeenView(APIView):
    def put(self, request):
        try:
            user = request.user
            privacy_settings, created = UserPrivacy.objects.get_or_create(
                user=user)
            privacy_settings.allow_last_seen = not privacy_settings.allow_last_seen
            privacy_settings.save()
            serializer = UserPrivacySerializer(privacy_settings)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": "Error in managing user last seen visibility", "full_error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
