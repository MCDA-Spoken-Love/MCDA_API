"""
Base test classes and utilities for the MCDA API project.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from apps.Account.models import Users
from apps.Privacy.models import UserPrivacy


class BaseTestCase(TestCase):
    """Base test case with common utilities"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.User = get_user_model()

    def create_user(self, username="testuser", email="test@example.com",
                    password="testpassword123", connection_code=None, **kwargs):
        """Helper method to create a user with sensible defaults"""
        if connection_code is None:
            connection_code = f"TEST{username[-2:].upper()}"

        user_data = {
            'username': username,
            'email': email,
            'password': password,
            'connection_code': connection_code,
            **kwargs
        }

        return Users.objects.create_user(**user_data)

    def create_multiple_users(self, count=3):
        """Helper method to create multiple users"""
        users = []
        for i in range(count):
            user = self.create_user(
                username=f"user{i+1}",
                email=f"user{i+1}@example.com",
                connection_code=f"USR{i+1:02d}"
            )
            users.append(user)
        return users

    def assertResponseError(self, response, expected_status=status.HTTP_400_BAD_REQUEST):
        """Assert that response contains an error with expected status"""
        self.assertEqual(response.status_code, expected_status)
        self.assertIn('message', response.data)

    def assertResponseSuccess(self, response, expected_status=status.HTTP_200_OK):
        """Assert that response is successful with expected status"""
        self.assertEqual(response.status_code, expected_status)


class BaseAPITestCase(APITestCase):
    """Base API test case with authentication utilities"""

    def setUp(self):
        super().setUp()
        self.client = APIClient()

    def create_user(self, username="testuser", email="test@example.com",
                    password="testpassword123", connection_code=None, **kwargs):
        """Helper method to create a user with sensible defaults"""
        if connection_code is None:
            connection_code = f"TEST{username[-2:].upper()}"

        user_data = {
            'username': username,
            'email': email,
            'password': password,
            'connection_code': connection_code,
            **kwargs
        }

        return Users.objects.create_user(**user_data)

    def authenticate_user(self, user):
        """Authenticate a user for API requests"""
        self.client.force_authenticate(user=user)
        return user

    def create_and_authenticate_user(self, username="testuser", email="test@example.com",
                                     password="testpassword123", **kwargs):
        """Create a user and authenticate them in one step"""
        user = self.create_user(username, email, password, **kwargs)
        self.authenticate_user(user)
        return user

    def create_privacy_settings(self, user, allow_status_visibility=True, allow_last_seen=True):
        """Helper method to create privacy settings for a user"""
        return UserPrivacy.objects.create(
            user=user,
            allow_status_visibility=allow_status_visibility,
            allow_last_seen=allow_last_seen
        )

    def assertResponseError(self, response, expected_status=status.HTTP_400_BAD_REQUEST):
        """Assert that response contains an error with expected status"""
        self.assertEqual(response.status_code, expected_status)
        self.assertIn('message', response.data)

    def assertResponseSuccess(self, response, expected_status=status.HTTP_200_OK):
        """Assert that response is successful with expected status"""
        self.assertEqual(response.status_code, expected_status)

    def assertUnauthorized(self, response):
        """Assert that response is unauthorized"""
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ModelTestMixin:
    """Mixin class for common model testing utilities"""

    def assertModelFieldExists(self, model, field_name):
        """Assert that a model has a specific field"""
        self.assertTrue(hasattr(model, field_name))

    def assertModelFieldType(self, model, field_name, field_type):
        """Assert that a model field is of a specific type"""
        field = model._meta.get_field(field_name)
        self.assertIsInstance(field, field_type)

    def assertModelFieldChoices(self, model, field_name, expected_choices):
        """Assert that a model field has specific choices"""
        field = model._meta.get_field(field_name)
        field_choices = [choice[0]
                         for choice in field.choices] if field.choices else []
        for choice in expected_choices:
            self.assertIn(choice, field_choices)


class SerializerTestMixin:
    """Mixin class for common serializer testing utilities"""

    def assertSerializerValid(self, serializer, data):
        """Assert that serializer is valid with given data"""
        test_serializer = serializer(data=data)
        self.assertTrue(test_serializer.is_valid(), test_serializer.errors)

    def assertSerializerInvalid(self, serializer, data, expected_errors=None):
        """Assert that serializer is invalid with given data"""
        test_serializer = serializer(data=data)
        self.assertFalse(test_serializer.is_valid())

        if expected_errors:
            for field, error in expected_errors.items():
                self.assertIn(field, test_serializer.errors)

    def assertSerializerFieldsPresent(self, serializer, instance, expected_fields):
        """Assert that serializer contains all expected fields"""
        test_serializer = serializer(instance)
        data = test_serializer.data

        for field in expected_fields:
            self.assertIn(field, data)


class DatabaseTestMixin:
    """Mixin class for database-related testing utilities"""

    def assertDatabaseCount(self, model, expected_count):
        """Assert that model has expected number of records in database"""
        actual_count = model.objects.count()
        self.assertEqual(actual_count, expected_count)

    def assertDatabaseEmpty(self, model):
        """Assert that model has no records in database"""
        self.assertDatabaseCount(model, 0)

    def assertObjectExists(self, model, **filters):
        """Assert that an object exists in database with given filters"""
        self.assertTrue(model.objects.filter(**filters).exists())

    def assertObjectDoesNotExist(self, model, **filters):
        """Assert that an object does not exist in database with given filters"""
        self.assertFalse(model.objects.filter(**filters).exists())


# Combined base classes for different types of tests
class BaseModelTest(BaseTestCase, ModelTestMixin, DatabaseTestMixin):
    """Base class for model tests"""
    pass


class BaseSerializerTest(BaseTestCase, SerializerTestMixin, ModelTestMixin):
    """Base class for serializer tests"""
    pass


class BaseViewTest(BaseAPITestCase, DatabaseTestMixin):
    """Base class for view tests"""
    pass
