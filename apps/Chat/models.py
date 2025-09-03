import uuid
from datetime import time

from django.db import models

from apps.Account.models import Users


class Chat(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_one = models.ForeignKey(
        Users, on_delete=models.CASCADE, related_name='chats_as_user_one')
    user_two = models.ForeignKey(
        Users, on_delete=models.CASCADE, related_name='chats_as_user_two')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    chat_duration = models.IntegerField(
        default=60)  # duration in minutes
    chat_open_time = models.TimeField(
        default=time(20, 0))

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user_one', 'user_two'], name='unique_chat')
        ]


class ChatMessages(models.Model):
    id = models.AutoField(primary_key=True)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    sender = models.ForeignKey(Users, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender.username} in chat {self.chat.id}"
