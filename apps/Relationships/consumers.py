import json

from services.websocket.consumer import BaseConsumer


class RelationshipConsumer(BaseConsumer):
    async def relationship_request_notification(self, event):
        await self.send(text_data=json.dumps(event['content']))
