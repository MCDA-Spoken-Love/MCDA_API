from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from Account.models import Users
from Privacy.models import UserPrivacy
from Privacy.serializer import UserPrivacySerializer


class UserPrivacyModelTest(TestCase):
    """Test UserPrivacy model functionality"""

    def setUp(self):
        self.user = Users.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123',
            connection_code='TEST01'
        )

    def test_create_privacy_settings(self):
        """Test creating privacy settings for a user"""
        privacy = UserPrivacy.objects.create(user=self.user)

        self.assertEqual(privacy.user, self.user)
        self.assertTrue(privacy.allow_status_visibility)  # Default value
        self.assertTrue(privacy.allow_last_seen)  # Default value
        self.assertIsNotNone(privacy.id)

    def test_privacy_settings_defaults(self):
        """Test that privacy settings have correct default values"""
        privacy = UserPrivacy.objects.create(user=self.user)

        self.assertTrue(privacy.allow_status_visibility)
        self.assertTrue(privacy.allow_last_seen)

    def test_privacy_settings_custom_values(self):
        """Test creating privacy settings with custom values"""
        privacy = UserPrivacy.objects.create(
            user=self.user,
            allow_status_visibility=False,
            allow_last_seen=False
        )

        self.assertFalse(privacy.allow_status_visibility)
        self.assertFalse(privacy.allow_last_seen)

    def test_privacy_settings_cascade_delete(self):
        """Test that privacy settings are deleted when user is deleted"""
        privacy = UserPrivacy.objects.create(user=self.user)
        privacy_id = privacy.id

        # Delete the user
        self.user.delete()

        # Privacy settings should be deleted too
        with self.assertRaises(UserPrivacy.DoesNotExist):
            UserPrivacy.objects.get(id=privacy_id)


class UserPrivacySerializerTest(TestCase):
    """Test UserPrivacySerializer functionality"""

    def setUp(self):
        self.user = Users.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123',
            connection_code='TEST01'
        )
        self.privacy = UserPrivacy.objects.create(user=self.user)

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
        data = {
            'user': self.user.id,
            'allow_status_visibility': False,
            'allow_last_seen': True
        }

        serializer = UserPrivacySerializer(data=data)
        self.assertTrue(serializer.is_valid())

        privacy = serializer.save()
        self.assertEqual(privacy.user, self.user)
        self.assertFalse(privacy.allow_status_visibility)
        self.assertTrue(privacy.allow_last_seen)


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
        self.privacy = UserPrivacy.objects.create(user=self.user)

    def test_get_privacy_settings_authenticated(self):
        """Test get_privacy_settings endpoint when authenticated"""
        self.client.force_authenticate(user=self.user)
        url = reverse('get_privacy_settings')
        response = self.client.get(url)

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
        """Test get_privacy_settings when user has no privacy record"""
        user_without_privacy = Users.objects.create_user(
            username='noprivacy',
            email='noprivacy@example.com',
            password='testpassword123',
            connection_code='TEST99'
        )

        self.client.force_authenticate(user=user_without_privacy)
        url = reverse('get_privacy_settings')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('message', response.data)

    def test_toggle_status_visibility_authenticated(self):
        """Test toggle_status_visibility endpoint when authenticated"""
        self.client.force_authenticate(user=self.user)
        original_value = self.privacy.allow_status_visibility

        url = reverse('toggle_status_visibility')
        response = self.client.put(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Refresh privacy object from database
        self.privacy.refresh_from_db()
        self.assertEqual(self.privacy.allow_status_visibility,
                         not original_value)

        # Response should contain updated data
        self.assertEqual(
            response.data['allow_status_visibility'], not original_value)

    def test_toggle_status_visibility_unauthenticated(self):
        """Test toggle_status_visibility endpoint when not authenticated"""
        url = reverse('toggle_status_visibility')
        response = self.client.put(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_toggle_last_seen_authenticated(self):
        """Test toggle_last_seen endpoint when authenticated"""
        self.client.force_authenticate(user=self.user)
        original_value = self.privacy.allow_last_seen

        url = reverse('toggle_last_seen')
        response = self.client.put(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Refresh privacy object from database
        self.privacy.refresh_from_db()
        self.assertEqual(self.privacy.allow_last_seen, not original_value)

        # Response should contain updated data
        self.assertEqual(response.data['allow_last_seen'], not original_value)

    def test_toggle_last_seen_unauthenticated(self):
        """Test toggle_last_seen endpoint when not authenticated"""
        url = reverse('toggle_last_seen')
        response = self.client.put(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_toggle_status_visibility_multiple_times(self):
        """Test toggling status visibility multiple times"""
        self.client.force_authenticate(user=self.user)
        url = reverse('toggle_status_visibility')

        # Get initial value
        initial_value = self.privacy.allow_status_visibility

        # Toggle first time
        response1 = self.client.put(url)
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.privacy.refresh_from_db()
        first_toggle_value = self.privacy.allow_status_visibility
        self.assertEqual(first_toggle_value, not initial_value)

        # Toggle second time (should return to original)
        response2 = self.client.put(url)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.privacy.refresh_from_db()
        second_toggle_value = self.privacy.allow_last_seen
        self.assertEqual(self.privacy.allow_status_visibility, initial_value)

    def test_toggle_last_seen_multiple_times(self):
        """Test toggling last seen multiple times"""
        self.client.force_authenticate(user=self.user)
        url = reverse('toggle_last_seen')

        # Get initial value
        initial_value = self.privacy.allow_last_seen

        # Toggle first time
        response1 = self.client.put(url)
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.privacy.refresh_from_db()
        first_toggle_value = self.privacy.allow_last_seen
        self.assertEqual(first_toggle_value, not initial_value)

        # Toggle second time (should return to original)
        response2 = self.client.put(url)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.privacy.refresh_from_db()
        self.assertEqual(self.privacy.allow_last_seen, initial_value)
