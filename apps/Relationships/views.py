
from datetime import date

from django.db.models import Q
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.Account.models import Users
from apps.Relationships.models import Relationship, RelationshipRequest
from apps.Relationships.serializer import RelationshipSerializer
from services.socket_message import send_socket_message


class ManageRelationshipsView(APIView):
    def get_relationships(self, user):
        relationship = Relationship.objects.filter(
            Q(user_one_id=user) | Q(user_two_id=user)
        )
        serializer = RelationshipSerializer(relationship, many=True).data
        return serializer

    def get(self, request):
        current_user = request.user
        try:
            relationship = self.get_relationships(current_user)
            return Response(relationship, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": "Error requesting user relationship", "full_error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        current_user = request.user
        try:
            relationship = self.get_relationships(current_user)
            if len(relationship):
                relationship.delete()
                return Response({"message": "You have ended things with your partner"}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "You don't have a relationship to terminate"}, status=status.HTTP_409_CONFLICT)
        except Exception as e:
            return Response({"message": "Error terminating relationship", "full_error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CreateRelationshipRequestView(APIView):
    def post(self, request):
        current_user = request.user
        try:
            connection_code = request.data.get('connection_code')
            if not connection_code:
                return Response({"message": "Please provide a connection code"}, status=status.HTTP_400_BAD_REQUEST)
            partner = Users.objects.get(connection_code=connection_code)
            request_obj = RelationshipRequest.objects.create(
                requester=Users.objects.get(pk=current_user.id),
                receiver=Users.objects.get(pk=partner.id),
                status='PENDING'
            )
            request_obj.save()
            send_socket_message(f"user_{partner.id}", 'relationship_request_notification', {
                'message': f'{current_user.first_name} has asked you to be in a loving relationship with you',
                'requester_id': str(current_user.id),
                'requester_name': current_user.first_name
            })

            return Response({"message": f"{current_user.first_name} has asked {partner.first_name} to be in a loving relationship with them!"}, status=status.HTTP_200_OK)

        except Exception as e:
            if 'Duplicate entry' in str(e):
                return Response({"message": "Error in creating relationship request", "full_error": 'Request already exists'}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"message": "Error in creating relationship request", "full_error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class RespondRelationshipRequestView(APIView):
    def post(self, request, pk):
        current_user = request.user
        today = date.today()

        try:
            if not pk:
                return Response({"message": "Please provide an existing request id"}, status=status.HTTP_400_BAD_REQUEST)

            accept = request.data.get('accept')
            relationship_request = RelationshipRequest.objects.get(pk=pk)

            if relationship_request.status != 'PENDING':
                return Response({"message": f"Relationship has already been {relationship_request.status.lower()}"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                partner = Users.objects.get(
                    pk=relationship_request.requester.id)
                if accept or str(accept).lower() == 'true':
                    relationship_start_date = request.data.get(
                        'relationship_start_date') or today
                    Relationship.objects.create(
                        user_one=relationship_request.requester,
                        user_two=relationship_request.receiver,
                        relationship_start_date=relationship_start_date
                    )
                    RelationshipRequest.objects.filter(
                        pk=pk).update(status='ACCEPTED')

                    send_socket_message(f"user_{partner.id}", 'relationship_request_notification', {
                        'message': f'{current_user.first_name} said yes! Congrats!',
                        'requester_id': str(current_user.id),
                        'requester_name': current_user.first_name
                    })

                    return Response({"message": f"{current_user.first_name} and {partner.first_name} are now dating! Congratulations!"}, status=status.HTTP_200_OK)

                elif not accept or str(accept).lower() == 'false':
                    RelationshipRequest.objects.filter(
                        pk=pk).update(status='REJECTED')

                    send_socket_message(f"user_{partner.id}", 'relationship_request_notification',  {
                        'message': f'{current_user.first_name} has said no, I\'m sorry...',
                        'requester_id': str(current_user.id),
                        'requester_name': current_user.first_name
                    })

                    return Response({"message": f"{current_user.first_name} has rejected {partner.first_name}'s love confession :("}, status=status.HTTP_200_OK)

        except Exception as e:
            if 'Duplicate entry' in str(e):
                return Response({"message": "Error in creating another relationship", "full_error": 'Request already accepted'}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"message": "Error in responding to relationship request", "full_error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
