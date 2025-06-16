
from datetime import date

from rest_framework import status
from rest_framework.decorators import (
    api_view,
)
from rest_framework.response import Response

from Account.models import Users
from Relationships.models import Relationship, RelationshipRequest


@api_view(['POST'])
def create_relationship_request(request):
    current_user = request.user
    try:
        connection_code = request.data.get('connection_code')
        if not connection_code:
            return Response({"message": "Please provide a connection code"}, status=status.HTTP_400_BAD_REQUEST)

        partner = Users.objects.get(connection_code=connection_code)
        if partner.id == current_user.id:
            return Response({"message": "Please provide a user code other than your own"}, status=status.HTTP_400_BAD_REQUEST)

        request = RelationshipRequest.objects.create(
            requester=Users.objects.get(pk=current_user.id), receiver=Users.objects.get(pk=partner.id), status='PENDING')
        request.save()

        return Response({"message": f"{current_user.first_name} has asked {partner.first_name} to be in a loving relationship with them!"}, status=status.HTTP_200_OK)

    except Exception as e:
        if 'Duplicate entry' in str(e):
            return Response({"message": "Error in creating relationship request", "full_error": 'Request already exists'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "Error in creating relationship request", "full_error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def respond_relationship_request(request, pk):
    current_user = request.user
    today = date.today()

    try:
        if not pk:
            return Response({"message": "Please provide an existing request id"}, status=status.HTTP_400_BAD_REQUEST)

        accept = request.data.get('accept')

        if accept is None:
            return Response({"message": "Please provide an appropriate response"}, status=status.HTTP_400_BAD_REQUEST)

        else:
            print('aqui', accept)
            relationship_request = RelationshipRequest.objects.get(
                pk=pk)
            print(relationship_request)
            partner = Users.objects.get(
                pk=relationship_request.requester.id)
            if accept is True:
                print('aqui de novo')
                relationship_start_date = request.data.get(
                    'relationship_start_date') if request.data.get('relationship_start_date') else today
                Relationship.objects.create(user_one=relationship_request.requester,
                                            user_two=relationship_request.receiver, relationship_start_date=relationship_start_date)

                RelationshipRequest.objects.filter(
                    pk=pk).update(status='ACCEPTED')
                return Response({"message": f"{current_user.first_name} and {partner.first_name} are now dating! Congratulations!"}, status=status.HTTP_200_OK)

            elif accept is False:
                RelationshipRequest.objects.filter(
                    pk=pk).update(status='REJECTED')
                return Response({"message": f"{current_user.first_name} has rejected {partner.first_name}'s love confession :("}, status=status.HTTP_200_OK)

    except Exception as e:
        print(e)
        return Response({"message": "Error in responding to relationship request", "full_error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
