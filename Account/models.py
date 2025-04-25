from enum import Enum

from django.contrib.auth.models import AbstractUser
from django.db import models


class Gender(Enum):
    CISMALE = 'CISMALE'
    CISFEMALE = 'CISFEMALE'
    TRANSMALE = 'TRANSMALE'
    TRANSFEMALE = 'TRANSFEMALE'
    NONBYNARY = 'NONBYNARY'
    INTERSEX = 'INTERSEX'
    AGENDER = 'AGENDER'
    OTHER = 'OTHER'
    PREFERNOTTOSAY = 'PREFERNOTTOSAY'

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class Sexuality(Enum):
    HETEROSEXUAL = 'HETEROSEXUAL'
    HOMOSEXUAL = 'HOMOSEXUAL'
    BISEXUAL = 'BISEXUAL'
    ASEXUAL = 'ASEXUAL'
    PANSEXUAL = 'PANSEXUAL'
    DEMISEXUAL = 'DEMISEXUAL'
    POLYSEXUAL = 'POLYSEXUAL'
    OTHER = 'OTHER'
    PREFERNOTTOSAY = 'PREFERNOTTOSAY'

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class Users(AbstractUser):
    id = models.AutoField(primary_key=True)
    password = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    gender = models.CharField(
        max_length=100, choices=Gender.choices(), null=True)
    sexuality = models.CharField(
        max_length=100, choices=Sexuality.choices(), null=True)
    connection_code = models.CharField(max_length=255, unique=True)
    partner_id = models.IntegerField(null=True)
    relation_ship_start_date = models.DateField(null=True)
    has_accepted_terms_and_conditions = models.BooleanField(default=False)
    has_accepted_privacy_policy = models.BooleanField(default=False)

    def __str__(self):
        return self.username


# class ChatTheme(Enum):
#     LIGHT = 'LIGHT'
#     DARK = 'DARK'
#     SYSTEM = 'SYSTEM'

#     @classmethod
#     def choices(cls):
#         return [(key.value, key.name) for key in cls]


# class Partner(models.Model):
#     id = models.AutoField(primary_key=True)
#     user = models.ForeignKey(Users, on_delete=models.CASCADE)
#     email = models.EmailField(max_length=255, unique=True)
#     username = models.CharField(max_length=255, unique=True)
#     first_name = models.CharField(max_length=255)
#     last_name = models.CharField(max_length=255, null=True)
#     gender = models.CharField(
#         max_length=100, choices=Gender.choices(), null=True)
#     sexuality = models.CharField(
#         max_length=100, choices=Sexuality.choices(), null=True)

#     def __str__(self):
#         return self.username


# class UserPrivacy(models.Model):
#     id = models.AutoField(primary_key=True)
#     user = models.ForeignKey(Users, on_delete=models.CASCADE)
#     allow_status_visibility = models.BooleanField(default=False)
#     allow_biometric = models.BooleanField(default=False)

#     def __str__(self):
#         return f"Privacy settings for {self.user.username}"


# class Chat(models.Model):
#     id = models.AutoField(primary_key=True)
#     first_user = models.ForeignKey(
#         Users, related_name='first_user', on_delete=models.CASCADE)
#     second_user = models.ForeignKey(
#         Users, related_name='second_user', on_delete=models.CASCADE)
#     color_scheme = models.CharField(max_length=255, null=True)
#     chat_duration = models.IntegerField(null=True)
#     chat_open_time = models.DateTimeField(null=True)
#     wallpaper = models.CharField(max_length=255, null=True)
#     theme = models.CharField(
#         max_length=10, choices=ChatTheme.choices(), null=True)

#     def __str__(self):
#         return f"Chat between {self.firstUser.username} and {self.secondUser.username}"


# class ChatMessages(models.Model):
#     id = models.AutoField(primary_key=True)
#     chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
#     sender = models.ForeignKey(Users, on_delete=models.CASCADE)
#     message = models.TextField()
#     timestamp = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Message from {self.sender.username} in chat {self.chat.id}"
