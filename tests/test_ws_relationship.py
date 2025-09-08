import json

import pytest
from channels.db import database_sync_to_async
from channels.routing import URLRouter
from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model
from django.test import TransactionTestCase

from apps.Relationships.routing import relationship_ws_urlpatterns

User = get_user_model()


@database_sync_to_async
def create_test_user():
    return User.objects.create_user(username="testuser", email="test@example.com", connection_code="TEST01", password="testpass")


@database_sync_to_async
def create_test_user_with_username(username, connection_code):
    return User.objects.create_user(username=username, email=f"{username}@example.com", connection_code=connection_code, password="testpass")


@database_sync_to_async
def create_relationship_request(requester, receiver):
    from apps.Relationships.models import RelationshipRequest
    return RelationshipRequest.objects.create(
        requester=requester,
        receiver=receiver,
        status="PENDING"
    )


@database_sync_to_async
def get_relationship_request(request_id):
    from apps.Relationships.models import RelationshipRequest
    return RelationshipRequest.objects.get(id=request_id)


@pytest.mark.asyncio
class TestRelationshipWebSocket(TransactionTestCase):
    @pytest.mark.asyncio
    async def test_ws_connection(self):
        """Test basic WebSocket connection and connection message"""
        user = await create_test_user()
        application = URLRouter(relationship_ws_urlpatterns)
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
    async def test_ws_send_relationship_request(self):
        """Test sending a relationship request through WebSocket"""
        # Create two users
        user1 = await create_test_user_with_username("testuser1", "TEST01")
        user2 = await create_test_user_with_username("testuser2", "TEST02")

        application = URLRouter(relationship_ws_urlpatterns)
        communicator = WebsocketCommunicator(
            application,
            "/ws/relationship-requests/"
        )
        communicator.scope["user"] = user1
        connected, _ = await communicator.connect()
        assert connected

        # Receive the initial "Connected!" message
        response = await communicator.receive_from()
        data = json.loads(response)
        assert data["message"] == "Connected!"

        # Send a relationship request message through WebSocket
        message_data = {
            "type": "relationship_request",
            "receiver_id": str(user2.id),
            "message": "Would you like to be in a relationship?"
        }
        await communicator.send_to(text_data=json.dumps(message_data))

        # Receive the echoed message from the base consumer
        response = await communicator.receive_from()
        data = json.loads(response)

        # Assert the message was echoed back correctly
        assert data["message"] == "Received"
        assert data["data"]["type"] == "relationship_request"
        assert data["data"]["receiver_id"] == str(user2.id)
        assert data["data"]["message"] == "Would you like to be in a relationship?"

        await communicator.disconnect()

    @pytest.mark.asyncio
    async def test_ws_accept_relationship_request(self):
        """Test accepting a relationship request through WebSocket"""
        # Create two users
        user1 = await create_test_user_with_username("testuser3", "TEST03")
        user2 = await create_test_user_with_username("testuser4", "TEST04")

        # Create a pending relationship request
        relationship_request = await create_relationship_request(user1, user2)

        application = URLRouter(relationship_ws_urlpatterns)
        communicator = WebsocketCommunicator(
            application,
            "/ws/relationship-requests/"
        )
        communicator.scope["user"] = user2  # Receiver accepts the request
        connected, _ = await communicator.connect()
        assert connected

        # Clear connection message
        await communicator.receive_from()

        # Send acceptance message through WebSocket
        message_data = {
            "type": "relationship_response",
            "request_id": str(relationship_request.id),
            "action": "accept",
            "relationship_start_date": "2025-09-08"
        }
        await communicator.send_to(text_data=json.dumps(message_data))

        # Receive the echoed message
        response = await communicator.receive_from()
        data = json.loads(response)

        # Assert the acceptance message was processed
        assert data["message"] == "Received"
        assert data["data"]["type"] == "relationship_response"
        assert data["data"]["action"] == "accept"
        assert data["data"]["request_id"] == str(relationship_request.id)

        await communicator.disconnect()

    @pytest.mark.asyncio
    async def test_ws_reject_relationship_request(self):
        """Test rejecting a relationship request through WebSocket"""
        # Create two users
        user1 = await create_test_user_with_username("testuser5", "TEST05")
        user2 = await create_test_user_with_username("testuser6", "TEST06")

        # Create a pending relationship request
        relationship_request = await create_relationship_request(user1, user2)

        application = URLRouter(relationship_ws_urlpatterns)
        communicator = WebsocketCommunicator(
            application,
            "/ws/relationship-requests/"
        )
        communicator.scope["user"] = user2  # Receiver rejects the request
        connected, _ = await communicator.connect()
        assert connected

        # Clear connection message
        await communicator.receive_from()

        # Send rejection message through WebSocket
        message_data = {
            "type": "relationship_response",
            "request_id": str(relationship_request.id),
            "action": "reject"
        }
        await communicator.send_to(text_data=json.dumps(message_data))

        # Receive the echoed message
        response = await communicator.receive_from()
        data = json.loads(response)

        # Assert the rejection message was processed
        assert data["message"] == "Received"
        assert data["data"]["type"] == "relationship_response"
        assert data["data"]["action"] == "reject"
        assert data["data"]["request_id"] == str(relationship_request.id)

        await communicator.disconnect()

    @pytest.mark.asyncio
    async def test_ws_relationship_notification_broadcast(self):
        """Test that relationship notifications are broadcasted to both users"""
        # Create two users
        user1 = await create_test_user_with_username("testuser7", "TEST07")
        user2 = await create_test_user_with_username("testuser8", "TEST08")

        application = URLRouter(relationship_ws_urlpatterns)

        # Connect both users to WebSocket
        communicator1 = WebsocketCommunicator(
            application, "/ws/relationship-requests/")
        communicator1.scope["user"] = user1
        connected1, _ = await communicator1.connect()
        assert connected1

        communicator2 = WebsocketCommunicator(
            application, "/ws/relationship-requests/")
        communicator2.scope["user"] = user2
        connected2, _ = await communicator2.connect()
        assert connected2

        # Clear connection messages
        await communicator1.receive_from()
        await communicator2.receive_from()

        # Send a relationship request from user1
        message_data = {
            "type": "relationship_request_notification",
            "sender": user1.username,
            "receiver": user2.username,
            "message": "New relationship request!"
        }
        await communicator1.send_to(text_data=json.dumps(message_data))

        # User1 should receive the echo
        response1 = await communicator1.receive_from()
        data1 = json.loads(response1)

        # Assert the echoed message structure
        assert data1["message"] == "Received"
        assert data1["data"]["type"] == "relationship_request_notification"
        assert data1["data"]["sender"] == user1.username
        assert data1["data"]["receiver"] == user2.username

        await communicator1.disconnect()
        await communicator2.disconnect()
