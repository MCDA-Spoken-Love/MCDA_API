from django.urls import re_path

from apps.Chat.consumers import ChatConsumer

chat_ws_urlpatterns = [re_path(r'ws/chat/$', ChatConsumer.as_asgi())]
