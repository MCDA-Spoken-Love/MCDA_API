from django.db.models import Q
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.Chat.serializer import ChatSerializer

from .models import Chat


class ChatView(APIView):
    serializer_class = ChatSerializer

    def get(self, request):
        current_user = request.user
        try:
            chat = Chat.objects.filter(
                Q(user_one_id=current_user) | Q(user_two_id=current_user)
            )
            serializer = self.serializer_class(chat, many=True)
            return Response(serializer.data[0])
        except Exception as e:
            return Response({"message": "Error fetching chat view", "full_error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        current_user = request.user
        try:
            if request.data.get('user_one') or request.data.get('user_two') or request.data.get('id'):
                return Response({"message": "You cannot update the chat users or id"}, status=status.HTTP_400_BAD_REQUEST)

            chat = Chat.objects.get(
                Q(user_one_id=current_user) | Q(user_two_id=current_user)
            )
            serializer = self.serializer_class(
                chat, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        except Exception as e:
            return Response({"message": "Error updating chat", "full_error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
