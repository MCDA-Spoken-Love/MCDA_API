from datetime import date, time

from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.Account.models import Users
from apps.Chat.models import Chat, ChatMessages
from apps.Chat.serializer import ChatMessagesSerializer, ChatSerializer
from apps.Relationships.models import Relationship


class ChatModelTest(TestCase):
    """Test chat model functionality"""

    def setUp(self):
        self.user1 = Users.objects.create_user(
            username='userchat1',
            email='userchat1@example.com',
            password='testpassword123',
            connection_code='USCH01'
        )
        self.user2 = Users.objects.create_user(
            username='userchat2',
            email='userchat2@example.com',
            password='testpassword123',
            connection_code='USCH02'
        )

    def test_create_chat(self):
        """Test creating a chat"""
        relationship = Relationship.objects.create(
            user_one=self.user1,
            user_two=self.user2,
            relationship_start_date=date.today()
        )
        chat = Chat.objects.get(
            user_one=self.user1,
            user_two=self.user2,
            relationship=relationship,
        )

        self.assertEqual(chat.user_one, self.user1)
        self.assertEqual(chat.user_two, self.user2)
        self.assertEqual(chat.relationship, relationship)
        self.assertEqual(chat.chat_duration, 60)
        self.assertEqual(chat.chat_open_time, time(20, 0))
        self.assertIsNotNone(chat.id)

    def test_unique_relationship_constraint(self):
        """Test for preventing duplicate chats"""
        # Creates relationship for automatic chat creation
        relationship = Relationship.objects.create(
            user_one=self.user1,
            user_two=self.user2,
        )

        # try to create duplicate chat
        with self.assertRaises(IntegrityError):
            Chat.objects.create(
                user_one=self.user1,
                user_two=self.user2,
                relationship=relationship
            )

    def test_chat_cascade_delete_user_one(self):
        """Test that chat is deleted when user_one is deleted"""
        relationship = Relationship.objects.create(
            user_one=self.user1,
            user_two=self.user2,
        )
        chat = Chat.objects.get(
            user_one=self.user1,
            user_two=self.user2,
            relationship=relationship
        )
        chat_id = chat.id

        # delete user one
        self.user1.delete()

        # chat should be deleted too
        with self.assertRaises(Chat.DoesNotExist):
            Chat.objects.get(id=chat_id)


class ChatMessagesModelTest(TestCase):
    """Test ChatMessages model functionality"""

    def setUp(self):
        self.user1 = Users.objects.create_user(
            username='userchat1',
            email='userchat1@example.com',
            password='testpassword123',
            connection_code='USCH01'
        )
        self.user2 = Users.objects.create_user(
            username='userchat2',
            email='userchat2@example.com',
            password='testpassword123',
            connection_code='USCH02'
        )
        self.relationship = Relationship.objects.create(
            user_one=self.user1,
            user_two=self.user2,
        )
        self.chat = Chat.objects.get(
            user_one=self.user1,
            user_two=self.user2,
            relationship=self.relationship
        )

    def test_create_chat_message(self):
        """Test create a chat message"""

        message = ChatMessages.objects.create(
            sender=self.user1,
            chat=self.chat,
            message='Hello there',
        )

        self.assertEqual(message.sender, self.user1)
        self.assertEqual(message.chat, self.chat)
        self.assertEqual(message.message, 'Hello there')
        self.assertIsNotNone(message.id)

    def test_create_empty_chat_message(self):
        """Tests failure when creating empty chat message"""
        with self.assertRaises(IntegrityError) as cm:
            ChatMessages.objects.create(
                sender=self.user1,
                chat=self.chat,
            )
        print('Exception raised: ', cm.exception, type(cm.exception))

    def test_message_cascade_delete_message_user_one(self):
        """Test that message is deleted when user_one is deleted"""
        message = ChatMessages.objects.create(
            sender=self.user1,
            chat=self.chat,
            message='Hello there',
        )
        message_id = message.id

        # delete user one
        self.user1.delete()

        # message should be deleted
        with self.assertRaises(ChatMessages.DoesNotExist):
            ChatMessages.objects.get(id=message_id)


class ChatSerializerTest(TestCase):
    """Test ChatSerializer functionality"""

    def setUp(self):
        self.user1 = Users.objects.create_user(
            username='userchat1',
            email='userchat1@example.com',
            password='testpassword123',
            connection_code='USCH01'
        )
        self.user2 = Users.objects.create_user(
            username='userchat2',
            email='userchat2@example.com',
            password='testpassword123',
            connection_code='USCH02'
        )
        self.relationship = Relationship.objects.create(
            user_one=self.user1,
            user_two=self.user2,
            relationship_start_date=date.today()
        )
        self.chat = Chat.objects.get(
            user_one=self.user1,
            user_two=self.user2,
            relationship=self.relationship
        )

    def test_serializer_contains_all_fields(self):
        """Test that serializer contains all model fields"""
        serializer = ChatSerializer(self.chat)
        data = serializer.data

        expected_fields = ['id', 'user_one', 'user_two',
                           'relationship', 'chat_duration', 'chat_open_time']

        for field in expected_fields:
            self.assertIn(field, data)

    def test_serializer_data_accuracy(self):
        """Test that serializer returns accurate data"""
        serializer = ChatSerializer(self.chat)
        data = serializer.data

        self.assertEqual(data['user_one'], self.user1.id)
        self.assertEqual(data['user_two'], self.user2.id)
        self.assertEqual(data['relationship'], self.relationship.id)
        self.assertEqual(data['chat_duration'], 60)
        self.assertEqual(data['chat_open_time'], str(time(20, 0)))


class ChatMessagesSerializerTest(TestCase):
    """Test ChatMessagesSerializer functionality"""

    def setUp(self):
        self.user1 = Users.objects.create_user(
            username='userchat1',
            email='userchat1@example.com',
            password='testpassword123',
            connection_code='USCH01'
        )
        self.user2 = Users.objects.create_user(
            username='userchat2',
            email='userchat2@example.com',
            password='testpassword123',
            connection_code='USCH02'
        )
        self.relationship = Relationship.objects.create(
            user_one=self.user1,
            user_two=self.user2,
            relationship_start_date=date.today()
        )
        self.chat = Chat.objects.get(
            user_one=self.user1,
            user_two=self.user2,
            relationship=self.relationship
        )
        self.message = ChatMessages.objects.create(
            sender=self.user1,
            chat=self.chat,
            message='Hello there',
        )

    def test_serializer_contains_all_fields(self):
        """Test that serializer contains all model fields"""
        serializer = ChatMessagesSerializer(self.message)
        data = serializer.data

        expected_fields = ['id', 'chat', 'sender',
                           'message', 'timestamp']

        for field in expected_fields:
            self.assertIn(field, data)

    def test_serializer_data_accuracy(self):
        """Test that serializer returns accurate data"""
        serializer = ChatMessagesSerializer(self.message)
        data = serializer.data

        self.assertEqual(data['sender'], self.user1.id)
        self.assertEqual(data['chat'], self.chat.id)
        self.assertEqual(data['message'], self.message.message)


class ChatViewsTest(APITestCase):
    """Test chat views functionality"""

    def setUp(self):
        self.user1 = Users.objects.create_user(
            username='userchat1',
            email='userchat1@example.com',
            password='testpassword123',
            connection_code='USCH01'
        )
        self.user2 = Users.objects.create_user(
            username='userchat2',
            email='userchat2@example.com',
            password='testpassword123',
            connection_code='USCH02'
        )
        self.relationship = Relationship.objects.create(
            user_one=self.user1,
            user_two=self.user2,
            relationship_start_date=date.today()
        )

    def test_get_chat(self):
        """Test GET chat"""
        self.client.force_authenticate(user=self.user1)
        url = reverse('chat')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        isinstance(response.data, dict)
        self.assertEqual(response.data['user_one'], self.user1.id)
        self.assertEqual(response.data['user_two'], self.user2.id)
        self.assertEqual(
            response.data['relationship'], self.relationship.id)

    def test_patch_chat_values(self):
        """Test PATCH chat with new values"""
        self.client.force_authenticate(user=self.user1)
        url = reverse('chat')
        data = {
            "chat_duration": 70,
            "chat_open_time": "19:10:00"
        }

        response = self.client.patch(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        chat = Chat.objects.get(
            user_one=self.user1,
            user_two=self.user2,
            relationship=self.relationship
        )

        self.assertEqual(chat.chat_duration, 70)
        self.assertEqual(chat.chat_open_time, time(19, 10))

    def test_change_chat_user_one(self):
        """Test patching chat with new user_one"""
        self.client.force_authenticate(user=self.user1)
        url = reverse('chat')
        data = {
            "user_one": self.user1.id,
        }

        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            'You cannot update the chat users, relationship or id', response.data['message'])

    def test_change_chat_user_two(self):
        """Test patching chat with new user_two"""
        self.client.force_authenticate(user=self.user1)
        url = reverse('chat')
        data = {
            "user_two": self.user1.id,
        }

        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            'You cannot update the chat users, relationship or id', response.data['message'])

    def test_change_chat_relationship(self):
        """Test patching chat with new relationship"""
        self.client.force_authenticate(user=self.user1)
        url = reverse('chat')
        data = {
            "relationship": self.relationship.id,
        }

        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            'You cannot update the chat users, relationship or id', response.data['message'])

    def test_change_chat_id(self):
        """Test patching chat with new id"""
        self.client.force_authenticate(user=self.user1)
        url = reverse('chat')
        data = {
            "id": self.relationship.id,
        }

        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            'You cannot update the chat users, relationship or id', response.data['message'])


class ChatMessagesViewTest(APITestCase):
    """Test ChatMessages view functionality"""

    def setUp(self):
        self.user1 = Users.objects.create_user(
            username='userchat1',
            email='userchat1@example.com',
            password='testpassword123',
            connection_code='USCH01'
        )
        self.user2 = Users.objects.create_user(
            username='userchat2',
            email='userchat2@example.com',
            password='testpassword123',
            connection_code='USCH02'
        )
        self.user3 = Users.objects.create_user(
            username='userchat3',
            email='userchat3@example.com',
            password='testpassword123',
            connection_code='USCH03'
        )
        self.relationship = Relationship.objects.create(
            user_one=self.user1,
            user_two=self.user2,
            relationship_start_date=date.today()
        )
        self.chat = Chat.objects.get(
            user_one=self.user1,
            user_two=self.user2,
            relationship=self.relationship
        )

    def test_list_messages_in_chat(self):
        """Test list paginated chat messages"""
        self.client.force_authenticate(user=self.user1)
        ChatMessages.objects.create(
            chat=self.chat, sender=self.user1, message="Hello!")
        ChatMessages.objects.create(
            chat=self.chat, sender=self.user2, message="Hi!")

        url = reverse("messages_paginated")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(response.data['results'][0]['message'], 'Hello!')
        self.assertEqual(response.data['results'][1]['message'], 'Hi!')

    def test_cursor_pagination_on_messages(self):
        """Test cursor pagination returns correct number of messages and next link"""
        self.client.force_authenticate(user=self.user1)

        # creates 100 messages
        for i in range(50):
            ChatMessages.objects.create(
                chat=self.chat,
                sender=self.user1,
                message=f'msg {i}'
            )
        for i in range(50):
            ChatMessages.objects.create(
                chat=self.chat,
                sender=self.user2,
                message=f'msg {i}'
            )

        url = reverse("messages_paginated")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check that only page_size messages are returned
        self.assertEqual(len(response.data['results']), 50)
        # Check that 'next' is present
        self.assertIn('next', response.data)
        self.assertIsNotNone(response.data['next'])

        # Fetch the next page using the 'next' cursor
        next_url = response.data['next']
        response2 = self.client.get(next_url)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response2.data['results']), 50)
        # There should still be a 'next' for the third page
        self.assertIn('next', response2.data)

    def test_get_message(self):
        """Test GET all of a chat's messages"""
        self.client.force_authenticate(user=self.user1)

        ChatMessages.objects.create(
            message='Hello there',
            chat=self.chat,
            sender=self.user1
        )
        url = reverse('messages')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['sender'], self.user1.id)

    def test_post_message(self):
        """Test POST a new message"""
        self.client.force_authenticate(user=self.user1)
        data = {"message": "hello there"}

        url = reverse('messages')
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        message = ChatMessages.objects.get(
            sender=self.user1,
            message=data['message'],
            chat=self.chat
        )

        self.assertEqual(message.message, 'hello there')
        self.assertEqual(message.sender.id, self.user1.id)
        self.assertEqual(message.chat.id, self.chat.id)

    def test_post_message_user_not_in_relationship(self):
        """Test POST a new message when user does not have a relationship"""
        self.client.force_authenticate(user=self.user3)
        data = {"message": "hello there"}

        url = reverse('messages')
        response = self.client.post(url, data)

        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn(
            'is not with anyone and cannot send a message', response.data['message'])
