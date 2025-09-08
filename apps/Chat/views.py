import logging

from django.db.models import Q
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.Account.serializer import CustomUserDetailsSerializer
from apps.Chat.serializer import ChatMessagesSerializer, ChatSerializer
from services.pagination import CursorPagination
from services.socket_message import send_socket_message

from .models import Chat, ChatMessages

logger = logging.getLogger("django")


def query_chat(user, patch_data=None):
    if patch_data is None:
        patch_data = {}
    try:
        chat = Chat.objects.get(Q(user_one_id=user) | Q(user_two_id=user))
        chat_serializer = ChatSerializer(chat, data=patch_data, partial=True)
        chat_serializer.is_valid(raise_exception=True)
        return chat_serializer
    except Exception as e:
        return Response({"message": "Error fetching chat", "full_error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ChatView(APIView):
    serializer_class = ChatSerializer

    def get(self, request):
        current_user = request.user
        try:
            chat = query_chat(current_user)
            return Response(chat.data)
        except Exception as e:
            return Response({"message": "Error fetching chat view", "full_error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        current_user = request.user
        try:
            if request.data.get('user_one') or request.data.get('user_two') or request.data.get('id') or request.data.get('relationship'):
                return Response({"message": "You cannot update the chat users, relationship or id"}, status=status.HTTP_400_BAD_REQUEST)
            chat = query_chat(current_user, request.data)
            chat.save()

            return Response(chat.data)

        except Exception as e:
            return Response({"message": "Error updating chat", "full_error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class MessagesView(APIView):

    def get(self, request):
        current_user = request.user
        try:
            chat = query_chat(current_user).data

            chat_messages = ChatMessages.objects.filter(
                chat_id=chat.get('id'))
            messages_serializer = ChatMessagesSerializer(
                chat_messages, many=True).data

            return Response(messages_serializer)
        except Exception as e:
            return Response({"message": "Error fetching chat messages", "full_error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        current_user = request.user
        try:
            chat = query_chat(current_user).data
            user_serialized = CustomUserDetailsSerializer(current_user).data
            if user_serialized["relationship"] is None:
                return Response({"message": f"{user_serialized['username']} is not with anyone and cannot send a message"}, status=status.HTTP_403_FORBIDDEN)

            relationship = user_serialized["relationship"]
            partner_id = relationship["partner"]["id"]
            partner_name = relationship['partner']['name']

            new_message = ChatMessages.objects.create(chat_id=chat.get(
                'id'), sender=current_user, message=request.data.get('message'))
            new_message_data = ChatMessagesSerializer(new_message).data

            send_socket_message(
                f'user_{partner_id}', "new_message_notification", {
                    'message': new_message_data['message'],
                    "sender": partner_name
                })
            return Response(new_message_data)
        except Exception as e:
            return Response({"message": "Error sending a new chat message", "full_error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class MessageList(ListAPIView):
    serializer_class = ChatMessagesSerializer
    pagination_class = CursorPagination

    def get_queryset(self):
        current_user = self.request.user
        chat = query_chat(current_user).data

        return ChatMessages.objects.filter(
            chat_id=chat.get('id'))
