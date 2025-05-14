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
            if username:
                all_users = Users.objects.filter(username=username)
            if email:
                all_users = Users.objects.filter(email=email)

        return Response({"user_count": len(all_users)}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"message": "Error in getting user by filter", "stack_trace": e}, status=status.HTTP_400_BAD_REQUEST)
