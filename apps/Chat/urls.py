from django.urls import path

from apps.Chat.views import ChatView, MessagesView

urlpatterns = [
    path('chat/', ChatView.as_view(), name='chat'),
    path('chat/messages/', MessagesView.as_view(), name='messages')
]
