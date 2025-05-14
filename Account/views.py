from rest_framework import status
from rest_framework.decorators import (
    api_view,
    permission_classes,
)
from rest_framework.response import Response

from Account.models import Users


@api_view(['GET'])
@permission_classes([])
def get_user_by_username(request, username):
    try:
        user = Users.objects.get(username=username)
        user_data = {
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
        }
        return Response(user_data, status=status.HTTP_200_OK)
    except Users.DoesNotExist:
        return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([])
def get_user_by_email(request, email):
    try:
        user = Users.objects.get(email=email)
        user_data = {
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
        }
        return Response(user_data, status=status.HTTP_200_OK)
    except Users.DoesNotExist:
        return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)
