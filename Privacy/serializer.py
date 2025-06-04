from rest_framework import serializers

from .models import UserPrivacy


class UserPrivacySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPrivacy
        fields = '__all__'
