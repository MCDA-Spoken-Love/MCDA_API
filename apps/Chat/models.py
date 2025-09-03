import uuid
from datetime import datetime, time

from django.db import models

from apps.Account.models import Users


def default_chat_open_time():
    now = datetime.now()
    return datetime.combine(now.date(), time(20, 0))

# Create your models here.


class Chat(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_one = models.ForeignKey(
        Users, on_delete=models.CASCADE, related_name='chats_as_user_one')
    user_two = models.ForeignKey(
        Users, on_delete=models.CASCADE, related_name='chats_as_user_two')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    wallpaper = models.CharField(max_length=255, null=True)
    chat_duration = models.IntegerField(
        default=60)  # duration in minutes
    chat_open_time = models.DateTimeField(
        default=default_chat_open_time())

    def __str__(self):
        return f"Chat between {self.user_one.username} and {self.user_two.username}"


class ChatMessages(models.Model):
    id = models.AutoField(primary_key=True)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    sender = models.ForeignKey(Users, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender.username} in chat {self.chat.id}"
