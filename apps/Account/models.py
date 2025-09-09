import uuid
from enum import Enum

from django.contrib.auth.models import AbstractUser
from django.db import models
from django_mysql.models import EnumField


class Gender(Enum):
    CISMALE = 'CISMALE'
    CISFEMALE = 'CISFEMALE'
    TRANSMALE = 'TRANSMALE'
    TRANSFEMALE = 'TRANSFEMALE'
    NONBINARY = 'NONBINARY'
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


GENDER_CHOICES = [e.value for e in Gender]
SEXUALITY_CHOICES = [e.value for e in Sexuality]


class Users(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    password = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    gender = EnumField(
        choices=GENDER_CHOICES, null=True)
    sexuality = EnumField(
        choices=SEXUALITY_CHOICES, null=True)
    connection_code = models.CharField(max_length=255, unique=True)
    has_accepted_terms_and_conditions = models.BooleanField(default=False)
    has_accepted_privacy_policy = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        from apps.Privacy.models import UserPrivacy
        UserPrivacy.objects.get_or_create(user=self)

    def __str__(self):
        return self.username
