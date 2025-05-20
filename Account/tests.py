from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from Account.models import Gender, Sexuality, Users
from Account.serializer import CustomRegisterSerializer, CustomUserDetailsSerializer
from Account.utils import email_to_code


class GenderEnumTest(TestCase):
    """Test Gender enum functionality"""

    def test_gender_choices(self):
        """Test that Gender enum returns proper choices"""
        choices = Gender.choices()
        self.assertIsInstance(choices, list)
        self.assertEqual(len(choices), 9)

        # Check some specific choices
        choice_values = [choice[0] for choice in choices]
        self.assertIn('CISMALE', choice_values)
        self.assertIn('CISFEMALE', choice_values)
        self.assertIn('NONBINARY', choice_values)


class SexualityEnumTest(TestCase):
    """Test Sexuality enum functionality"""

    def test_sexuality_choices(self):
        """Test that Sexuality enum returns proper choices"""
        choices = Sexuality.choices()
        self.assertIsInstance(choices, list)
        self.assertEqual(len(choices), 9)

        # Check some specific choices
        choice_values = [choice[0] for choice in choices]
        self.assertIn('HETEROSEXUAL', choice_values)
        self.assertIn('HOMOSEXUAL', choice_values)
        self.assertIn('BISEXUAL', choice_values)


class UsersModelTest(TestCase):
    """Test Users model functionality"""

    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpassword123',
            'gender': 'CISMALE',
            'sexuality': 'HETEROSEXUAL',
            'connection_code': 'TEST01',
            'has_accepted_terms_and_conditions': True,
            'has_accepted_privacy_policy': True
        }

    def test_create_user(self):
        """Test creating a user"""
        user = Users.objects.create_user(**self.user_data)
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.gender, 'CISMALE')
        self.assertTrue(user.has_accepted_terms_and_conditions)
        self.assertIsNotNone(user.id)  # UUID field

    def test_user_str_method(self):
        """Test user string representation"""
        user = Users.objects.create_user(**self.user_data)
        self.assertEqual(str(user), 'testuser')

    def test_unique_email_constraint(self):
        """Test that email must be unique"""
        Users.objects.create_user(**self.user_data)

        # Try to create another user with same email
        duplicate_data = self.user_data.copy()
        duplicate_data['username'] = 'different_username'

        with self.assertRaises(Exception):
            Users.objects.create_user(**duplicate_data)

    def test_unique_connection_code_constraint(self):
        """Test that connection_code must be unique"""
        Users.objects.create_user(**self.user_data)

        # Try to create another user with same connection_code
        duplicate_data = self.user_data.copy()
        duplicate_data['username'] = 'different_username'
        duplicate_data['email'] = 'different@example.com'

        with self.assertRaises(Exception):
            Users.objects.create_user(**duplicate_data)


class EmailToCodeUtilTest(TestCase):
    """Test email_to_code utility function"""

    def test_email_to_code_returns_6_chars(self):
        """Test that email_to_code returns exactly 6 characters"""
        code = email_to_code('test@example.com')
        self.assertEqual(len(code), 6)
        self.assertTrue(code.isupper())

    def test_email_to_code_consistency(self):
        """Test that same email always produces same code"""
        email = 'test@example.com'
        code1 = email_to_code(email)
        code2 = email_to_code(email)
        self.assertEqual(code1, code2)

    def test_different_emails_different_codes(self):
        """Test that different emails produce different codes"""
        code1 = email_to_code('test1@example.com')
        code2 = email_to_code('test2@example.com')
        self.assertNotEqual(code1, code2)


class CustomRegisterSerializerTest(TestCase):
    """Test CustomRegisterSerializer functionality"""

    def setUp(self):
        self.valid_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'username': 'john_doe',
            'password1': 'strongpassword123',
            'password2': 'strongpassword123',
            'gender': 'CISMALE',
            'sexuality': 'HETEROSEXUAL',
            'has_accepted_terms_and_conditions': True,
            'has_accepted_privacy_policy': True
        }

    def test_valid_serializer(self):
        """Test serializer with valid data"""
        serializer = CustomRegisterSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())

    def test_password_mismatch_validation(self):
        """Test validation fails when passwords don't match"""
        invalid_data = self.valid_data.copy()
        invalid_data['password2'] = 'differentpassword'

        serializer = CustomRegisterSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)

    def test_duplicate_email_validation(self):
        """Test validation fails for duplicate email"""
        # Create a user first
        Users.objects.create_user(
            username='existing',
            email='john@example.com',
            password='password123'
        )

        serializer = CustomRegisterSerializer(data=self.valid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)

    def test_duplicate_username_validation(self):
        """Test validation fails for duplicate username"""
        # Create a user first
        Users.objects.create_user(
            username='john_doe',
            email='different@example.com',
            password='password123'
        )

        serializer = CustomRegisterSerializer(data=self.valid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('username', serializer.errors)


class AccountViewsTest(APITestCase):
    """Test Account views functionality"""

    def setUp(self):
        self.client = APIClient()
        self.user = Users.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123',
            connection_code='TEST01'
        )
        self.other_user = Users.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpassword123',
            connection_code='TEST02'
        )

    def test_get_user_by_filter_with_username(self):
        """Test get_user_by_filter endpoint with username"""
        url = reverse('get_user_by_username')
        response = self.client.get(url, {'username': 'testuser'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user_count'], 1)

    def test_get_user_by_filter_with_email(self):
        """Test get_user_by_filter endpoint with email"""
        url = reverse('get_user_by_username')
        response = self.client.get(url, {'email': 'test@example.com'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user_count'], 1)

    def test_get_user_by_filter_with_both_params(self):
        """Test get_user_by_filter endpoint with both username and email"""
        url = reverse('get_user_by_username')
        response = self.client.get(url, {
            'username': 'testuser',
            'email': 'test@example.com'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user_count'], 1)

    def test_get_user_by_filter_no_params(self):
        """Test get_user_by_filter endpoint without parameters"""
        url = reverse('get_user_by_username')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('message', response.data)

    def test_get_user_by_filter_nonexistent_user(self):
        """Test get_user_by_filter endpoint with nonexistent user"""
        url = reverse('get_user_by_username')
        response = self.client.get(url, {'username': 'nonexistent'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user_count'], 0)

    def test_manage_user_delete_authenticated(self):
        """Test manage_user DELETE endpoint when authenticated"""
        self.client.force_authenticate(user=self.user)
        url = reverse('manage_user')
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('successfully deleted', response.data['message'])

        # Verify user is actually deleted
        with self.assertRaises(Users.DoesNotExist):
            Users.objects.get(id=self.user.id)

    def test_manage_user_delete_unauthenticated(self):
        """Test manage_user DELETE endpoint when not authenticated"""
        url = reverse('manage_user')
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class CustomUserDetailsSerializerTest(TestCase):
    """Test CustomUserDetailsSerializer functionality"""

    def setUp(self):
        self.user = Users.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123',
            gender='CISMALE',
            sexuality='HETEROSEXUAL'
        )

    def test_serializer_contains_expected_fields(self):
        """Test that serializer contains all expected fields"""
        serializer = CustomUserDetailsSerializer(self.user)
        data = serializer.data

        # Check that all important fields are present
        expected_fields = ['id', 'username', 'email', 'gender', 'sexuality',
                           'connection_code', 'has_accepted_terms_and_conditions',
                           'has_accepted_privacy_policy']

        for field in expected_fields:
            self.assertIn(field, data)

    def test_serializer_excludes_sensitive_fields(self):
        """Test that serializer properly handles sensitive data"""
        serializer = CustomUserDetailsSerializer(self.user)
        data = serializer.data

        # Password should not be exposed in the serialized data
        self.assertNotIn('password', data)

        # But other important fields should be present
        self.assertIn('username', data)
        self.assertIn('email', data)
        self.assertIn('id', data)
