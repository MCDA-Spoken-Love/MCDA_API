import json

import pytest
from channels.routing import URLRouter
from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model
from django.test import TransactionTestCase

from Relationships.routing import websocket_urlpatterns

User = get_user_model()


@pytest.mark.asyncio
class TestRelationshipWebSocket(TransactionTestCase):
    @pytest.mark.asyncio
    async def test_ws_connection(self):
        """Test basic WebSocket connection and connection message"""
        application = URLRouter(websocket_urlpatterns)
        communicator = WebsocketCommunicator(
            application, "/ws/relationship-requests/"
        )
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
        application = URLRouter(websocket_urlpatterns)
        communicator = WebsocketCommunicator(
            application, "/ws/relationship-requests/"
        )
        connected, _ = await communicator.connect()
        assert connected

        # Discard the initial "Connected!" message
        initial = await communicator.receive_from()
        initial_data = json.loads(initial)
        assert initial_data["message"] == "Connected!"

        # Send a message to the consumer
        test_message = {"test": "hello"}
        await communicator.send_to(text_data=json.dumps(test_message))

        # Receive the echoed message
        response = await communicator.receive_from()
        data = json.loads(response)
        assert data["message"] == "Received"
        assert data["data"] == test_message

        await communicator.disconnect()
