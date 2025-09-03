import json

import pytest
from channels.db import database_sync_to_async
from channels.routing import URLRouter
from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model
from django.test import TransactionTestCase

from apps.Relationships.routing import websocket_urlpatterns

User = get_user_model()


@database_sync_to_async
def create_test_user():
    return User.objects.create_user(username="testuser", password="testpass")


@pytest.mark.asyncio
class TestRelationshipWebSocket(TransactionTestCase):
    @pytest.mark.asyncio
    async def test_ws_connection(self):
        """Test basic WebSocket connection and connection message"""
        user = await create_test_user()
        application = URLRouter(websocket_urlpatterns)
        communicator = WebsocketCommunicator(
            application,
            "/ws/relationship-requests/"
        )
        communicator.scope["user"] = user
        connected, _ = await communicator.connect()
        assert connected

        # Receive the initial "Connected!" message
        response = await communicator.receive_from()
        data = json.loads(response)
        assert data["message"] == "Connected!"

        await communicator.disconnect()

    @pytest.mark.asyncio
    async def test_ws_send_message(self):
        """Test sending a message to the WebSocket"""
        user = await create_test_user()
        application = URLRouter(websocket_urlpatterns)
        communicator = WebsocketCommunicator(
            application,
            "/ws/relationship-requests/"
        )
        communicator.scope["user"] = user
        connected, _ = await communicator.connect()
        assert connected

        response = await communicator.receive_from()
        data = json.loads(response)
        assert data["message"] == "Connected!"

        await communicator.disconnect()
