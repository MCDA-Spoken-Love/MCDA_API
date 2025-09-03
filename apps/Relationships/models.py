from enum import Enum

from django.db import models
from django_mysql.models import EnumField

from apps.Account.models import Users


class Status(Enum):
    ACCEPTED = 'ACCEPTED'
    PENDING = 'PENDING'
    REJECTED = 'REJECTED'

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


STATUS_CHOICES = [e.value for e in Status]


class Relationship(models.Model):
    id = models.AutoField(primary_key=True)
    user_one = models.ForeignKey(
        Users,
        on_delete=models.CASCADE,
        related_name='relationships_as_user_one'
    )
    user_two = models.ForeignKey(
        Users,
        on_delete=models.CASCADE,
        related_name='relationships_as_user_two'
    )
    relationship_start_date = models.DateField(null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user_one', 'user_two'], name='unique_relationship')
        ]


class RelationshipRequest(models.Model):
    id = models.AutoField(primary_key=True)
    status = EnumField(choices=STATUS_CHOICES, default=Status.PENDING)
    requester = models.ForeignKey(
        Users,
        on_delete=models.CASCADE,
        null=True,
        related_name='requester'
    )
    receiver = models.ForeignKey(
        Users,
        on_delete=models.CASCADE,
        null=True,
        related_name='receiver'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['requester', 'receiver'], name='unique_relationship_request')
        ]
