from allauth.account.adapter import get_adapter
from allauth.utils import get_username_max_length
from django.db import transaction
from rest_framework import serializers

from Account.models import Gender, Sexuality, Users
from Account.utils import email_to_code


class CustomRegisterSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=30)
    last_name = serializers.CharField(max_length=30)
    email = serializers.EmailField(max_length=255, required=True)
    gender = serializers.ChoiceField(choices=Gender.choices(), required=False)
    sexuality = serializers.ChoiceField(
        choices=Sexuality.choices(), required=False)
    has_accepted_terms_and_conditions = serializers.BooleanField(default=False)
    has_accepted_privacy_policy = serializers.BooleanField(default=False)
    username = serializers.CharField(
        max_length=get_username_max_length(), required=True)

    password1 = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)

    def validate_email(self, email):
        email = get_adapter().clean_email(email)
        if not email:
            raise serializers.ValidationError(
                "Email is required.")
        if Users.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                "Email already exists.")

        return email

    def validate_username(self, username):
        if not username:
            raise serializers.ValidationError(
                "Username is required.")
        if Users.objects.filter(username=username).exists():
            raise serializers.ValidationError(
                "Username already exists.")
        return username

    def validate_password1(self, password):
        return get_adapter().clean_password(password)

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError(
                ("The two password fields didn't match."))
        return data

    def custom_signup(self, request, user):
        user.first_name = self.validated_data['first_name']
        user.last_name = self.validated_data['last_name']
        user.email = self.validated_data['email']
        user.username = self.validated_data['username']
        user.password1 = self.validated_data['password1']
        user.password2 = self.validated_data['password2']
        user.gender = self.validated_data['gender']
        user.sexuality = self.validated_data['sexuality']
        user.connection_code = email_to_code(self.validated_data['email'])
        user.has_accepted_terms_and_conditions = self.validated_data[
            'has_accepted_terms_and_conditions']
        user.has_accepted_privacy_policy = self.validated_data['has_accepted_privacy_policy']
        user.username = self.validated_data['username']
        user.save()
        return user

    def get_cleaned_data(self):
        return {
            'email': self.validated_data['email'],
            'password1': self.validated_data['password2'],
            'password2': self.validated_data['password2'],
            'first_name': self.validated_data['first_name'],
            'last_name': self.validated_data['last_name'],
            'gender': self.validated_data['gender'],
            'sexuality': self.validated_data['sexuality'],
            'has_accepted_terms_and_conditions': self.validated_data['has_accepted_terms_and_conditions'],
            'has_accepted_privacy_policy': self.validated_data['has_accepted_privacy_policy'],
            'username': self.validated_data['username'],
        }

    @transaction.atomic
    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        adapter.save_user(request, user, self)
        self.custom_signup(request, user)
        user.save()
        return user


class PartnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ('id',  'username', 'email',
                  'first_name', 'last_name', 'gender', 'sexuality', 'connection_code',
                  'relation_ship_start_date')


class CustomUserDetailsSerializer(serializers.ModelSerializer):
    partner = PartnerSerializer(read_only=True)

    class Meta:
        model = Users
        # add fields as needed
        fields = "__all__"
