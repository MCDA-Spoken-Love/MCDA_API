from django.db import models

from Account.models import Users


class UserPrivacy(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    allow_status_visibility = models.BooleanField(default=True)
    allow_last_seen = models.BooleanField(default=True)

    def __str__(self):
        return self
