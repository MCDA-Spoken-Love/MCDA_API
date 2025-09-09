import json

from services.websocket.consumer import BaseConsumer


class ChatConsumer(BaseConsumer):
    async def connect(self):
        chat_id = self.scope["url_route"]["kwargs"]["chat_id"]
        self.scope["chat_id"] = chat_id  # Add to scope for later use
        user = self.scope['user']
        await self.channel_layer.group_add(
            f'chat_{chat_id}',
            self.channel_name
        )
        if user.is_authenticated:
            # Notify group that user is online
            await self.channel_layer.group_send(
                f"chat_{chat_id}",
                {
                    "type": "user_status",
                    "user_id": str(user.id),
                    "online": True,
                }
            )
        await super().connect()

    async def disconnect(self, close_code):
        user = self.scope['user']
        chat_id = self.scope["url_route"]["kwargs"]["chat_id"]
        await self.channel_layer.group_discard(f"chat_{chat_id}", self.channel_name)
        if user.is_authenticated:
            # Notify group that user is offline
            await self.channel_layer.group_send(
                f"chat_{chat_id}",
                {
                    "type": "user_status",
                    "user_id": str(user.id),
                    "online": False,
                }
            )

    async def new_message_notification(self, event):
        await self.send(text_data=json.dumps({
            "type": "new_message_notification",
            "message": {
                "user_id": str(event["user_id"]),
                "sender": event["sender"],
                "chat_message": event["message"]
            }
        }))

    async def typing_status(self, event):
        await self.send(text_data=json.dumps({
            "type": "typing_status",
            "message": {
                "user_id": str(event["user_id"]),
                "is_typing": event["is_typing"],
            }}))

    async def user_status(self, event):
        await self.send(text_data=json.dumps({
            "type": "user_status",
            "message": {
                "user_id": event["user_id"],
                "online": event["online"],
            }
        }))

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)

        if data.get('type') == 'typing':
            await self.channel_layer.group_send(
                f'chat_{data['chat_id']}',
                {
                    "type": "typing_status",
                    "user_id": str(self.scope['user'].id),
                    "is_typing": data.get("is_typing", False)
                }
            )
        elif data.get('type') == 'user_status':
            await self.channel_layer.group_send(
                f'chat_{data['chat_id']}',
                {
                    "type": "user_status",
                    "user_id": str(self.scope['user'].id),
                    "online": data.get("online", False)
                }
            )
        elif data.get('type') == 'new_message_notification':
            await self.channel_layer.group_send(
                f'chat_{data['chat_id']}',
                {
                    "type": "new_message_notification",
                    "user_id": str(self.scope['user'].id),
                    "message": data.get("message"),
                    "sender": data.get('sender')
                }
            )
