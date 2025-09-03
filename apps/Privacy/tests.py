from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from apps.Account.models import Users
from apps.Privacy.models import UserPrivacy
from apps.Privacy.serializer import UserPrivacySerializer


class UserPrivacyModelTest(TestCase):
    """Test UserPrivacy model functionality"""

    def test_create_privacy_settings(self):
        """Test creating privacy settings for a user"""
        user = Users.objects.create_user(
            username='testuser1',
            email='test1@example.com',
            password='testpassword123',
            connection_code='TEST01'
        )
        # Use get_or_create since the User model automatically creates privacy settings
        privacy, created = UserPrivacy.objects.get_or_create(user=user)

        self.assertEqual(privacy.user, user)
        self.assertTrue(privacy.allow_status_visibility)  # Default value
        self.assertTrue(privacy.allow_last_seen)  # Default value
        self.assertIsNotNone(privacy.id)

    def test_privacy_settings_defaults(self):
        """Test that privacy settings have correct default values"""
        user = Users.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpassword123',
            connection_code='TEST02'
        )
        # Use get_or_create since the User model automatically creates privacy settings
        privacy, created = UserPrivacy.objects.get_or_create(user=user)

        self.assertTrue(privacy.allow_status_visibility)
        self.assertTrue(privacy.allow_last_seen)

    def test_privacy_settings_custom_values(self):
        """Test creating privacy settings with custom values"""
        user = Users.objects.create_user(
            username='testuser3',
            email='test3@example.com',
            password='testpassword123',
            connection_code='TEST03'
        )
        # Get the automatically created privacy record and update it
        privacy = UserPrivacy.objects.get(user=user)
        privacy.allow_status_visibility = False
        privacy.allow_last_seen = False
        privacy.save()

        # Verify the custom values
        privacy.refresh_from_db()
        self.assertFalse(privacy.allow_status_visibility)
        self.assertFalse(privacy.allow_last_seen)

    def test_privacy_settings_cascade_delete(self):
        """Test that privacy settings are deleted when user is deleted"""
        user = Users.objects.create_user(
            username='testuser4',
            email='test4@example.com',
            password='testpassword123',
            connection_code='TEST04'
        )
        # Get the automatically created privacy record
        privacy = UserPrivacy.objects.get(user=user)
        privacy_id = privacy.id

        # Delete the user
        user.delete()

        # Privacy settings should be deleted too
        with self.assertRaises(UserPrivacy.DoesNotExist):
            UserPrivacy.objects.get(id=privacy_id)

    def test_one_to_one_constraint(self):
        """Test that only one UserPrivacy can exist per user"""
        user = Users.objects.create_user(
            username='testuser5',
            email='test5@example.com',
            password='testpassword123',
            connection_code='TEST05'
        )
        # Privacy record should already exist from User.save() method
        existing_privacy = UserPrivacy.objects.get(user=user)
        self.assertIsNotNone(existing_privacy)

        # Attempting to create another should raise an IntegrityError
        # Could be IntegrityError or ValidationError
        with self.assertRaises(Exception):
            UserPrivacy.objects.create(user=user)


class UserPrivacySerializerTest(TestCase):
    """Test UserPrivacySerializer functionality"""

    def setUp(self):
        self.user = Users.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123',
            connection_code='TEST01'
        )
        self.privacy, created = UserPrivacy.objects.get_or_create(
            user=self.user)

    def test_serializer_contains_all_fields(self):
        """Test that serializer contains all model fields"""
        serializer = UserPrivacySerializer(self.privacy)
        data = serializer.data

        expected_fields = ['id', 'user',
                           'allow_status_visibility', 'allow_last_seen']
        for field in expected_fields:
            self.assertIn(field, data)

    def test_serializer_data_accuracy(self):
        """Test that serializer returns accurate data"""
        serializer = UserPrivacySerializer(self.privacy)
        data = serializer.data

        self.assertEqual(data['user'], self.user.id)
        self.assertEqual(data['allow_status_visibility'],
                         self.privacy.allow_status_visibility)
        self.assertEqual(data['allow_last_seen'], self.privacy.allow_last_seen)

    def test_serializer_deserialization(self):
        """Test deserializing data back to model"""
        # Create a completely new user to avoid constraint violations
        unique_user = Users.objects.create_user(
            username='uniqueuser',
            email='unique@example.com',
            password='testpassword123',
            connection_code='UNIQ01'
        )

        # Get the automatically created UserPrivacy record
        user_privacy, created = UserPrivacy.objects.get_or_create(
            user=unique_user)

        # Test updating an existing UserPrivacy record
        data = {
            'allow_status_visibility': False,
            'allow_last_seen': True
        }

        serializer = UserPrivacySerializer(
            instance=user_privacy, data=data, partial=True)
        if not serializer.is_valid():
            print("Serializer errors:", serializer.errors)
        self.assertTrue(serializer.is_valid())

        # Save and check the instance
        instance = serializer.save()
        self.assertIsInstance(instance, UserPrivacy)
        self.assertEqual(instance.user, unique_user)
        self.assertEqual(instance.allow_status_visibility, False)
        self.assertEqual(instance.allow_last_seen, True)


class PrivacyViewsTest(APITestCase):
    """Test Privacy views functionality"""

    def setUp(self):
        self.client = APIClient()
        self.user = Users.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123',
            connection_code='TEST01'
        )
        # Don't create privacy record here - let the views handle it

    def test_get_privacy_settings_authenticated(self):
        """Test get_privacy_settings endpoint when authenticated"""
        self.client.force_authenticate(user=self.user)
        print(self.user)
        url = reverse('get_privacy_settings')
        print(url)
        response = self.client.get(url)
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user'], self.user.id)
        self.assertIn('allow_status_visibility', response.data)
        self.assertIn('allow_last_seen', response.data)

    def test_get_privacy_settings_unauthenticated(self):
        """Test get_privacy_settings endpoint when not authenticated"""
        url = reverse('get_privacy_settings')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_privacy_settings_no_privacy_record(self):
        """Test get_privacy_settings when user has no privacy record - should create one"""
        user_without_privacy = Users.objects.create_user(
            username='noprivacy',
            email='noprivacy@example.com',
            password='testpassword123',
            connection_code='TEST99'
        )

        self.client.force_authenticate(user=user_without_privacy)
        url = reverse('get_privacy_settings')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('allow_status_visibility', response.data)
        self.assertIn('allow_last_seen', response.data)

    def test_toggle_status_visibility_authenticated(self):
        """Test toggle_status_visibility endpoint when authenticated"""
        self.client.force_authenticate(user=self.user)

        # First call should create the privacy record and toggle from default True to False
        url = reverse('toggle_status_visibility')
        response = self.client.put(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['allow_status_visibility'])

    def test_toggle_status_visibility_unauthenticated(self):
        """Test toggle_status_visibility endpoint when not authenticated"""
        url = reverse('toggle_status_visibility')
        response = self.client.put(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_toggle_last_seen_authenticated(self):
        """Test toggle_last_seen endpoint when authenticated"""
        self.client.force_authenticate(user=self.user)

        # First call should create the privacy record and toggle from default True to False
        url = reverse('toggle_last_seen')
        response = self.client.put(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['allow_last_seen'])

    def test_toggle_last_seen_unauthenticated(self):
        """Test toggle_last_seen endpoint when not authenticated"""
        url = reverse('toggle_last_seen')
        response = self.client.put(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_toggle_status_visibility_multiple_times(self):
        """Test toggling status visibility multiple times"""
        self.client.force_authenticate(user=self.user)
        url = reverse('toggle_status_visibility')

        # First toggle (True -> False)
        response1 = self.client.put(url)
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertFalse(response1.data['allow_status_visibility'])

        # Second toggle (False -> True)
        response2 = self.client.put(url)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertTrue(response2.data['allow_status_visibility'])

    def test_toggle_last_seen_multiple_times(self):
        """Test toggling last seen multiple times"""
        self.client.force_authenticate(user=self.user)
        url = reverse('toggle_last_seen')

        # First toggle (True -> False)
        response1 = self.client.put(url)
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertFalse(response1.data['allow_last_seen'])

        # Second toggle (False -> True)
        response2 = self.client.put(url)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertTrue(response2.data['allow_last_seen'])
