
from rest_framework import status
from rest_framework.decorators import (
    api_view,
)
from rest_framework.response import Response

from Privacy.models import UserPrivacy
from Privacy.serializer import UserPrivacySerializer


@api_view(['GET'])
def get_privacy_settings(request):
    try:
        user = request.user
        privacy_settings = UserPrivacy.objects.get(user=user)
        serializer = UserPrivacySerializer(privacy_settings)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"message": "Error in getting user status visibility", "full_error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def toggle_status_visibility(request):
    try:
        user = request.user
        privacy_settings = UserPrivacy.objects.get(user=user)
        privacy_settings.allow_status_visibility = not privacy_settings.allow_status_visibility
        privacy_settings.save()
        serializer = UserPrivacySerializer(privacy_settings)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"message": "Error in managing user status visibility", "full_error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def toggle_last_seen(request):
    try:
        user = request.user
        privacy_settings = UserPrivacy.objects.get(user=user)
        privacy_settings.allow_last_seen = not privacy_settings.allow_last_seen
        privacy_settings.save()
        serializer = UserPrivacySerializer(privacy_settings)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"message": "Error in managing user last seen visibility", "full_error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
