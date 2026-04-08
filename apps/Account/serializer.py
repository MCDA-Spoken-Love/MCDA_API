from allauth.account.adapter import get_adapter
from allauth.utils import get_username_max_length
from django.db import transaction
from django.db.models import Q
from rest_framework import serializers

from apps.Account.models import Gender, Sexuality, Users
from apps.Account.utils import email_to_code


class CustomRegisterSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=30)
    last_name = serializers.CharField(max_length=30)
    email = serializers.EmailField(max_length=255, required=True)
    gender = serializers.ChoiceField(choices=Gender.choices, required=False)
    sexuality = serializers.ChoiceField(choices=Sexuality.choices, required=False)
    has_accepted_terms_and_conditions = serializers.BooleanField(default=False)
    has_accepted_privacy_policy = serializers.BooleanField(default=False)
    username = serializers.CharField(
        max_length=get_username_max_length(), required=True
    )
    profile_picture = serializers.ImageField(write_only=True, required=False)

    password1 = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)

    def validate_email(self, email):
        email = get_adapter().clean_email(email)
        if not email:
            raise serializers.ValidationError("Email é obrigatório.")
        if Users.objects.filter(email=email).exists():
            raise serializers.ValidationError("Email já existe.")

        return email

    def validate_username(self, username):
        if not username:
            raise serializers.ValidationError("Username é obrigatório.")
        if Users.objects.filter(username=username).exists():
            raise serializers.ValidationError("Username já existe.")
        return username

    def validate_password1(self, password):
        return get_adapter().clean_password(password)

    def validate(self, data):
        if data["password1"] != data["password2"]:
            raise serializers.ValidationError("As senha devem ser iguais.")
        return data

    def custom_signup(self, user):
        user.first_name = self.validated_data["first_name"]
        user.last_name = self.validated_data["last_name"]
        user.email = self.validated_data["email"]
        user.username = self.validated_data["username"]
        user.password1 = self.validated_data["password1"]
        user.password2 = self.validated_data["password2"]

        user.connection_code = email_to_code(self.validated_data["email"])
        user.has_accepted_terms_and_conditions = self.validated_data[
            "has_accepted_terms_and_conditions"
        ]
        user.has_accepted_privacy_policy = self.validated_data[
            "has_accepted_privacy_policy"
        ]
        user.username = self.validated_data["username"]

        if self.validated_data.get("sexuality"):
            user.sexuality = self.validated_data["sexuality"]

        if self.validated_data.get("gender"):
            user.gender = self.validated_data["gender"]

        if self.validated_data.get("profile_picture"):
            user.profile_picture = self.validated_data["profile_picture"]

        user.save()
        return user

    def get_cleaned_data(self):
        return {
            "email": self.validated_data["email"],
            "password1": self.validated_data["password2"],
            "password2": self.validated_data["password2"],
            "first_name": self.validated_data["first_name"],
            "last_name": self.validated_data["last_name"],
            "gender": self.validated_data.get("gender", ""),
            "sexuality": self.validated_data.get("sexuality", ""),
            "profile_picture": self.validated_data.get("profile_picture", ""),
            "has_accepted_terms_and_conditions": self.validated_data[
                "has_accepted_terms_and_conditions"
            ],
            "has_accepted_privacy_policy": self.validated_data[
                "has_accepted_privacy_policy"
            ],
            "username": self.validated_data["username"],
        }

    @transaction.atomic
    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        adapter.save_user(request, user, self)
        self.custom_signup(user)
        user.save()

        return user


class UserAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ["gender", "sexuality", "profile_picture"]

    def validate(self, attrs):
        allowed_fields = set(self.fields.keys())
        incoming_fields = set(self.initial_data.keys())
        extra_fields = incoming_fields - allowed_fields
        if extra_fields:
            raise serializers.ValidationError(
                f"Os seguintes campos não são permitidos: {', '.join(extra_fields)}"
            )
        return super().validate(attrs)


class CustomUserDetailsSerializer(serializers.ModelSerializer):
    relationship = serializers.SerializerMethodField()

    class Meta:
        model = Users
        exclude = ("password",)  # Exclude password for security
        read_only_fields = (
            "id",
            "date_joined",
            "last_login",
            "is_superuser",
            "is_staff",
        )

    def get_relationship(self, obj):
        from apps.Relationships.models import Relationship

        rel = Relationship.objects.filter(Q(user_one=obj) | Q(user_two=obj)).first()
        if rel:
            if rel.user_one.username == obj.username:
                partner = rel.user_two
            else:
                partner = rel.user_one

            return {
                "relationship_start_date": rel.relationship_start_date,
                "partner": {
                    "name": partner.first_name + " " + partner.last_name,
                    "username": partner.username,
                    "id": partner.id,
                },
            }
        else:
            return None
