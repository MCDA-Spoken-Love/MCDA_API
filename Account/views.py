from datetime import date

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


@api_view(['GET', 'POST', 'PUT', 'DELETE'])
def manager_user_relationshop(request):
    current_user = request.user
    today = date.today()
    try:
        if request.method == 'POST' or request.method == 'PUT':
            connection_code = request.data.get('connection_code')
            if not connection_code:
                return Response({"message": "Please provide a connection code"}, status=status.HTTP_400_BAD_REQUEST)

            partner = Users.objects.get(connection_code=connection_code)
            Users.objects.filter(id=current_user.id).update(
                partner=partner.id, relation_ship_start_date=today)
            Users.objects.filter(id=partner.id).update(
                partner=current_user.id, relation_ship_start_date=today)

            return Response({"message": f"{current_user.first_name} and {partner.first_name} are now dating! Congratulations!"}, status=status.HTTP_200_OK)

        if request.method == 'DELETE':
            partner = Users.objects.get(id=current_user.partner.id)
            if not partner:
                return Response({"message": "No partner found"}, status=status.HTTP_400_BAD_REQUEST)
            Users.objects.filter(id=current_user.id).update(
                partner=None, relation_ship_start_date=None)

            Users.objects.filter(id=current_user.partner.id).update(
                partner=None, relation_ship_start_date=None)

            return Response({"message": f"{current_user.first_name} and {partner.first_name} are no longer dating!"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"message": "Error in managing user relationship", "stack_trace": e}, status=status.HTTP_400_BAD_REQUEST)
