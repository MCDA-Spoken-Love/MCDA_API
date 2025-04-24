from enum import Enum

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


class ChatTheme(Enum):
    LIGHT = 'LIGHT'
    DARK = 'DARK'
    SYSTEM = 'SYSTEM'

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class Users(models.Model):
    id = models.AutoField(primary_key=True)
    userName = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    firstName = models.CharField(max_length=255)
    lastName = models.CharField(max_length=255, null=True)
    gender = models.CharField(
        max_length=100, choices=Gender.choices(), null=True)
    sexuality = models.CharField(
        max_length=100, choices=Sexuality.choices(), null=True)
    connectionCode = models.CharField(max_length=255, unique=True)
    partnerId = models.IntegerField(null=True)
    relationShipStartDate = models.DateField(null=True)
    hasAcceptedTermsAndConditions = models.BooleanField(default=False)
    hasAcceptedPrivacyPolicy = models.BooleanField(default=False)

    def __str__(self):
        return self.userName


class Partner(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    email = models.EmailField(max_length=255, unique=True)
    userName = models.CharField(max_length=255, unique=True)
    firstName = models.CharField(max_length=255)
    lastName = models.CharField(max_length=255, null=True)
    gender = models.CharField(
        max_length=100, choices=Gender.choices(), null=True)
    sexuality = models.CharField(
        max_length=100, choices=Sexuality.choices(), null=True)

    def __str__(self):
        return self.userName


class UserPrivacy(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    allowStatusVisibility = models.BooleanField(default=False)
    allowBiometric = models.BooleanField(default=False)

    def __str__(self):
        return f"Privacy settings for {self.user.userName}"


class Chat(models.Model):
    id = models.AutoField(primary_key=True)
    firstUser = models.ForeignKey(
        Users, related_name='first_user', on_delete=models.CASCADE)
    secondUser = models.ForeignKey(
        Users, related_name='second_user', on_delete=models.CASCADE)
    colorScheme = models.CharField(max_length=255, null=True)
    chatDuration = models.IntegerField(null=True)
    chatOpenTime = models.DateTimeField(null=True)
    wallpaper = models.CharField(max_length=255, null=True)
    theme = models.CharField(
        max_length=10, choices=ChatTheme.choices(), null=True)

    def __str__(self):
        return f"Chat between {self.firstUser.userName} and {self.secondUser.userName}"


class ChatMessages(models.Model):
    id = models.AutoField(primary_key=True)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    sender = models.ForeignKey(Users, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender.userName} in chat {self.chat.id}"
