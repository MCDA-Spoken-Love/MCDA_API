import json

import pytest
from channels.db import database_sync_to_async
from channels.routing import URLRouter
from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model
from django.test import TransactionTestCase

from apps.Chat.routing import chat_ws_urlpatterns

User = get_user_model()


@database_sync_to_async
def create_test_user():
    return User.objects.create_user(username="testuser", password="testpass")


@database_sync_to_async
def create_test_user_with_username(username, connection_code):
    return User.objects.create_user(username=username, email=f"{username}@example.com", connection_code=connection_code, password="testpass")


@database_sync_to_async
def create_test_relationship_and_chat(user1, user2):
    from datetime import date

    from apps.Chat.models import Chat
    from apps.Relationships.models import Relationship

    # Create relationship
    relationship = Relationship.objects.create(
        user_one=user1,
        user_two=user2,
        relationship_start_date=date.today()
    )

    # Get the auto-created chat (created by Relationship.save())
    chat = Chat.objects.get(relationship=relationship)

    return relationship, chat


@pytest.mark.asyncio
class TestChatMessagesWebSocket(TransactionTestCase):
    @pytest.mark.asyncio
    async def test_ws_connection(self):
        """Test basic WebSocket connection and connection message"""
        user = await create_test_user()
        application = URLRouter(chat_ws_urlpatterns)
        communicator = WebsocketCommunicator(
            application,
            "/ws/chat/"
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
        """Test sending a chat message through WebSocket"""
        # Create two users for the chat
        user1 = await create_test_user_with_username("testuser1", 'TESTU1')
        user2 = await create_test_user_with_username("testuser2", 'TESTU2')

        # Create relationship and chat between users
        relationship, chat = await create_test_relationship_and_chat(user1, user2)

        application = URLRouter(chat_ws_urlpatterns)
        communicator = WebsocketCommunicator(
            application,
            "/ws/chat/"
        )
        communicator.scope["user"] = user1
        connected, _ = await communicator.connect()
        assert connected

        # Receive the initial "Connected!" message
        response = await communicator.receive_from()
        data = json.loads(response)
        assert data["message"] == "Connected!"

        # Send a chat message through WebSocket
        message_data = {
            "type": "new_message_notification",
            "message": "Hello from WebSocket!",
            "chat_id": str(chat.id)
        }
        await communicator.send_to(text_data=json.dumps(message_data))

        # Receive the echoed message from the base consumer
        response = await communicator.receive_from()
        data = json.loads(response)

        # Assert the message was echoed back correctly
        assert data["message"] == "Received"
        assert data["data"]["type"] == "new_message_notification"
        assert data["data"]["message"] == "Hello from WebSocket!"
        assert data["data"]["chat_id"] == str(chat.id)

        await communicator.disconnect()

    @pytest.mark.asyncio
    async def test_ws_message_broadcast_to_multiple_users(self):
        """Test that messages are broadcasted to all users in the chat"""
        # Create two users for the chat
        user1 = await create_test_user_with_username("testuser3", 'TESTU3')
        user2 = await create_test_user_with_username("testuser4", 'TESTU4')

        # Create relationship and chat between users
        relationship, chat = await create_test_relationship_and_chat(user1, user2)

        application = URLRouter(chat_ws_urlpatterns)

        # Connect both users to the WebSocket
        communicator1 = WebsocketCommunicator(application, "/ws/chat/")
        communicator1.scope["user"] = user1
        connected1, _ = await communicator1.connect()
        assert connected1

        communicator2 = WebsocketCommunicator(application, "/ws/chat/")
        communicator2.scope["user"] = user2
        connected2, _ = await communicator2.connect()
        assert connected2

        # Clear connection messages
        await communicator1.receive_from()
        await communicator2.receive_from()

        # Send message from user1
        message_data = {
            "type": "new_message_notification",
            "message": "Hello from user1!",
            "chat_id": str(chat.id)
        }
        await communicator1.send_to(text_data=json.dumps(message_data))

        # User1 should receive the echo from their own message
        response1 = await communicator1.receive_from()
        data1 = json.loads(response1)

        # Assert the echoed message structure
        assert data1["message"] == "Received"
        assert data1["data"]["message"] == "Hello from user1!"
        assert data1["data"]["type"] == "new_message_notification"

        await communicator1.disconnect()
        await communicator2.disconnect()
