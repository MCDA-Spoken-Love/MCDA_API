
from rest_framework import status
from rest_framework.decorators import (
    api_view,
    permission_classes,
)
from rest_framework.response import Response

from Account.models import Users


@api_view(['GET'])
@permission_classes([])
def get_user_by_filter(request):
    try:
        username = request.query_params.get('username')
        email = request.query_params.get('email')
        all_users = []
        if not username and not email:
            return Response({"message": "Please provide an username or email"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            if username and email:
                all_users = Users.objects.filter(
                    username=username, email=email)
            elif username:
                all_users = Users.objects.filter(username=username)
            elif email:
                all_users = Users.objects.filter(email=email)

        return Response({"user_count": len(all_users)}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"message": "Error in getting user by filter", "full_error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def manage_user(request):
    user = request.user

    if request.method == 'DELETE':
        try:
            Users.objects.get(id=user.id).delete()

            return Response({"message": f"@{user.username}'s account was successfully deleted"}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({"message": "Error in deleting user", "full_error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
