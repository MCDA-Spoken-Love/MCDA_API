import json

from services.websocket.consumer import BaseConsumer


class ChatConsumer(BaseConsumer):
    async def new_message_notification(self, event):
        await self.send(text_data=json.dumps(event['content']))
