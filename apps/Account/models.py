import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


class Gender(models.TextChoices):
    CISMALE = "CISMALE", "Homem Cis"
    CISFEMALE = "CISFEMALE", "Mulher Cis"
    TRANSMALE = "TRANSMALE", "Homem Trans"
    TRANSFEMALE = "TRANSFEMALE", "Mulher Trans"
    NONBINARY = "NONBINARY", "Não binaria"
    OTHER = "OTHER", "Outro"
    PREFERNOTTOSAY = "PREFERNOTTOSAY", "Prefiro não dizer"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class Sexuality(models.TextChoices):
    HETEROSEXUAL = "HETEROSEXUAL", "Heterossexual"
    HOMOSEXUAL = "HOMOSEXUAL", "Homossexual"
    BISEXUAL = "BISEXUAL", "Bissexual"
    ASEXUAL = "ASEXUAL", "Assexual"
    PANSEXUAL = "PANSEXUAL", "Pansexual"
    OTHER = "OTHER", "Outro"
    PREFERNOTTOSAY = "PREFERNOTTOSAY", "Prefiro não dizer"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class Users(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    password = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    gender = models.CharField(
        max_length=255, choices=Gender.choices, blank=True, default=""
    )
    sexuality = models.CharField(
        max_length=255, choices=Sexuality.choices, blank=True, default=""
    )
    profile_picture = models.URLField(max_length=255, blank=True, default="")

    connection_code = models.CharField(max_length=255, unique=True)
    has_accepted_terms_and_conditions = models.BooleanField(default=False)
    has_accepted_privacy_policy = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        from apps.Privacy.models import UserPrivacy

        UserPrivacy.objects.get_or_create(user=self)

    def __str__(self):
        return self.username
