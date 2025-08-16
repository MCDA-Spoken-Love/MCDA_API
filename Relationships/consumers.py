

import json
import logging

from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser

logger = logging.getLogger("django")


class RelationshipConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope.get('user', AnonymousUser())
        self.group_name = f"user_{getattr(self.user, 'id', 'anon')}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        await self.send(text_data=json.dumps({"message": "Connected!"}))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        await self.send(text_data=json.dumps(
            {"message": "Received", "data": text_data_json}))

    async def relationship_request_notification(self, event):
        logger.warning('event: %s', event)
        await self.send(text_data=json.dumps(event['content']))
