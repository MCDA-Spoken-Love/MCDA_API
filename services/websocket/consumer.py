import json

from channels.generic.websocket import AsyncWebsocketConsumer


class BaseConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            self.user = self.scope["user"]

            # Check if user is authenticated
            if not self.user or self.user.is_anonymous:
                await self.close(code=403)
                return

            self.group_name = f"user_{getattr(self.user, 'id')}"
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
            await self.send(text_data=json.dumps({"message": "Connected!"}))
        except Exception:
            await self.close(code=1011)  # Internal error

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        await self.send(text_data=json.dumps(
            {"message": "Received", "data": text_data_json}))
