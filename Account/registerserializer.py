from rest_framework import serializers
from allauth.utils import (get_username_max_length)
from allauth.account import app_settings as allauth_settings
from allauth.account.adapter import get_adapter
from django.db import transaction

from allauth.account.models import EmailAddress
from Account.models import Gender, Sexuality, Users

class CustomRegisterSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=30)
    last_name = serializers.CharField(max_length=30)
    email = serializers.EmailField(max_length=255, required=True)
    password = serializers.CharField(max_length=128, write_only=True)
    gender = serializers.ChoiceField(choices=Gender.choices(), required=False)
    sexuality = serializers.ChoiceField(choices=Sexuality.choices(), required=False)
    connection_code = serializers.CharField(max_length=255, required=True)
    partner_id = serializers.IntegerField(required=False)
    relation_ship_start_date = serializers.DateField(required=False)
    has_accepted_terms_and_conditions = serializers.BooleanField(default=False)
    has_accepted_privacy_policy = serializers.BooleanField(default=False)
    username = serializers.CharField(
        max_length=get_username_max_length(), required=True)

    def validate_email(self,email):
        email = get_adapter().clean_email(email)
        print(f'--------------{email}------------------')
        if not email:
            raise serializers.ValidationError(
                "Email is required.")
        if Users.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                "Email already exists.")

        return email

    def validate_connection_code(self, connection_code):
        if not connection_code:
            raise serializers.ValidationError(
                "Connection code is required.")
        if len(connection_code) < 6:
            raise serializers.ValidationError(
                "Connection code must be at least 6 characters long.")
        if Users.objects.filter(connection_code=connection_code).exists():
            raise serializers.ValidationError(
                "Connection code already exists.")
        return connection_code

    def validate_username(self, username):
        if not username:
            raise serializers.ValidationError(
                "Username is required.")
        if Users.objects.filter(username=username).exists():
            raise serializers.ValidationError(
                "Username already exists.")
        return username

    def custom_signup(self,request,user):
        user.first_name = self.validated_data['first_name']
        user.last_name = self.validated_data['last_name']
        user.email = self.validated_data['email']
        user.username = self.validated_data['username']
        user.password = self.validated_data['password']
        user.gender = self.validated_data['gender']
        user.sexuality = self.validated_data['sexuality']
        user.connection_code = self.validated_data['connection_code']
        user.partner_id = self.validated_data['partner_id']
        user.relation_ship_start_date = self.validated_data['relation_ship_start_date']
        user.has_accepted_terms_and_conditions = self.validated_data['has_accepted_terms_and_conditions']
        user.has_accepted_privacy_policy = self.validated_data['has_accepted_privacy_policy']
        user.username = self.validated_data['username']
        user.save()
        return user

    def get_cleaned_data(self):
        return {
            'email': self.validated_data['email'],
            'password': self.validated_data['password'],
            'first_name': self.validated_data['first_name'],
            'last_name': self.validated_data['last_name'],
            'gender': self.validated_data['gender'],
            'sexuality': self.validated_data['sexuality'],
            'connection_code': self.validated_data['connection_code'],
            'partner_id': self.validated_data['partner_id'],
            'relation_ship_start_date': self.validated_data['relation_ship_start_date'],
            'has_accepted_terms_and_conditions': self.validated_data['has_accepted_terms_and_conditions'],
            'has_accepted_privacy_policy': self.validated_data['has_accepted_privacy_policy'],
            'username': self.validated_data['username'],
        }


    @transaction.atomic
    def save(self,request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        adapter.save_user(request, user, self)
        self.custom_signup(request, user)
        user.save()
        return user
