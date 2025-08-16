
from datetime import date

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import (
    api_view,
)
from rest_framework.response import Response

from Account.models import Users
from Relationships.models import Relationship, RelationshipRequest
from Relationships.serializer import RelationshipSerializer


@api_view(['GET', 'POST', 'PUT', 'DELETE'])
def manage_relationships(request):
    current_user = request.user
    if request.method == 'GET':
        try:
            relationship = Relationship.objects.filter(
                Q(user_one_id=current_user) | Q(user_two_id=current_user)
            )
            serializer = RelationshipSerializer(
                relationship, many=True).data
            return Response(serializer, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": "Error requesting user relationship", "full_error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        try:
            relationship = Relationship.objects.filter(
                Q(user_one_id=current_user) | Q(user_two_id=current_user)
            )
            serializer = RelationshipSerializer(
                relationship, many=True).data
            if len(serializer):
                relationship.delete()
                return Response({"message": "You have ended things with your partner"}, status=status.HTTP_200_OK)

            else:
                return Response({"message": "You don't have a relationship to terminate"}, status=status.HTTP_409_CONFLICT)

        except Exception as e:
            return Response({"message": "Error terminating relationship", "full_error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


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

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'user_{partner.id}',
            {
                'type': 'relationship_request_notification',
                'content': {
                    'message': f'{current_user.first_name} has asked you to be in a loving relationship with you',
                    'requester_id': str(current_user.id),
                    'requester_name': current_user.first_name
                }
            }
        )

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
            relationship_request = RelationshipRequest.objects.get(
                pk=pk)
            partner = Users.objects.get(
                pk=relationship_request.requester.id)
            if accept or str(accept).lower() == 'true':
                relationship_start_date = request.data.get(
                    'relationship_start_date') if request.data.get('relationship_start_date') else today
                Relationship.objects.create(user_one=relationship_request.requester,
                                            user_two=relationship_request.receiver, relationship_start_date=relationship_start_date)

                RelationshipRequest.objects.filter(
                    pk=pk).update(status='ACCEPTED')
                return Response({"message": f"{current_user.first_name} and {partner.first_name} are now dating! Congratulations!"}, status=status.HTTP_200_OK)

            elif not accept or str(accept).lower() == 'false':
                RelationshipRequest.objects.filter(
                    pk=pk).update(status='REJECTED')
                return Response({"message": f"{current_user.first_name} has rejected {partner.first_name}'s love confession :("}, status=status.HTTP_200_OK)

            else:
                return Response({"message": "Invalid value for accept parameter"}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        if 'Duplicate entry' in str(e):
            return Response({"message": "Error in creating another relationship", "full_error": 'Request already accepted'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": "Error in responding to relationship request", "full_error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
