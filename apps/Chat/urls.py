from django.urls import path

from apps.Chat.views import ChatView, MessageList, MessagesView, PartnerStatusView

urlpatterns = [
    path('chat/', ChatView.as_view(), name='chat'),
    path('chat/messages/', MessagesView.as_view(), name='messages'),
    path('chat/messages/paginated/',
         MessageList.as_view(), name='messages_paginated'),
    path('chat/is_partner_online/<uuid:user_id>/',
         PartnerStatusView.as_view(), name='partner_status')
]
