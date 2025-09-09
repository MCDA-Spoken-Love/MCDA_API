from datetime import date

from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from apps.Account.models import Users
from apps.Relationships.models import Relationship, RelationshipRequest, Status
from apps.Relationships.serializer import RelationshipSerializer


class StatusEnumTest(TestCase):
    """Test Status enum functionality"""

    def test_status_choices(self):
        """Test that Status enum returns proper choices"""
        choices = Status.choices()
        self.assertIsInstance(choices, list)

        # Check some specific choices
        choice_values = [choice[0] for choice in choices]
        self.assertIn('ACCEPTED', choice_values)
        self.assertIn('PENDING', choice_values)
        self.assertIn('REJECTED', choice_values)


class RelationshipModelTest(TestCase):
    """Test Relationship model functionality"""

    def setUp(self):
        self.user1 = Users.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='testpassword123',
            connection_code='USER01'
        )
        self.user2 = Users.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='testpassword123',
            connection_code='USER02'
        )
        self.user3 = Users.objects.create_user(
            username='user3',
            email='user3@example.com',
            password='testpassword123',
            connection_code='USER03'
        )

    def test_create_relationship(self):
        """Test creating a relationship"""
        relationship = Relationship.objects.create(
            user_one=self.user1,
            user_two=self.user2,
            relationship_start_date=date.today()
        )

        self.assertEqual(relationship.user_one, self.user1)
        self.assertEqual(relationship.user_two, self.user2)
        self.assertEqual(relationship.relationship_start_date, date.today())
        self.assertIsNotNone(relationship.id)

    def test_relationship_without_start_date(self):
        """Test creating a relationship without start date"""
        relationship = Relationship.objects.create(
            user_one=self.user1,
            user_two=self.user2
        )

        self.assertEqual(relationship.user_one, self.user1)
        self.assertEqual(relationship.user_two, self.user2)
        self.assertIsNone(relationship.relationship_start_date)

    def test_unique_relationship_constraint(self):
        """Test that unique constraint prevents duplicate relationships"""
        # Create first relationship
        Relationship.objects.create(
            user_one=self.user1,
            user_two=self.user2
        )

        # Try to create duplicate relationship
        with self.assertRaises(IntegrityError):
            Relationship.objects.create(
                user_one=self.user1,
                user_two=self.user2
            )

    def test_relationship_cascade_delete_user_one(self):
        """Test that relationship is deleted when user_one is deleted"""
        relationship = Relationship.objects.create(
            user_one=self.user1,
            user_two=self.user2
        )
        relationship_id = relationship.id

        # Delete user_one
        self.user1.delete()

        # Relationship should be deleted too
        with self.assertRaises(Relationship.DoesNotExist):
            Relationship.objects.get(id=relationship_id)


class RelationshipRequestModelTest(TestCase):
    """Test RelationshipRequest model functionality"""

    def setUp(self):
        self.requester = Users.objects.create_user(
            username='requester',
            email='requester@example.com',
            password='testpassword123',
            connection_code='REQ001'
        )
        self.receiver = Users.objects.create_user(
            username='receiver',
            email='receiver@example.com',
            password='testpassword123',
            connection_code='REC001'
        )

    def test_create_relationship_request(self):
        """Test creating a relationship request"""
        request = RelationshipRequest.objects.create(
            requester=self.requester,
            receiver=self.receiver,
            status='PENDING'
        )

        self.assertEqual(request.requester, self.requester)
        self.assertEqual(request.receiver, self.receiver)
        self.assertEqual(request.status, 'PENDING')
        self.assertIsNotNone(request.id)

    def test_unique_relationship_request_constraint(self):
        """Test that unique constraint prevents duplicate relationship requests"""
        # Create first request
        RelationshipRequest.objects.create(
            requester=self.requester,
            receiver=self.receiver,
            status='PENDING'
        )

        # Try to create duplicate request
        with self.assertRaises(IntegrityError):
            RelationshipRequest.objects.create(
                requester=self.requester,
                receiver=self.receiver,
                status='PENDING'
            )


class RelationshipSerializerTest(TestCase):
    """Test RelationshipSerializer functionality"""

    def setUp(self):
        self.user1 = Users.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='testpassword123',
            connection_code='USER01'
        )
        self.user2 = Users.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='testpassword123',
            connection_code='USER02'
        )
        self.relationship = Relationship.objects.create(
            user_one=self.user1,
            user_two=self.user2,
            relationship_start_date=date.today()
        )

    def test_serializer_contains_all_fields(self):
        """Test that serializer contains all model fields"""
        serializer = RelationshipSerializer(self.relationship)
        data = serializer.data

        expected_fields = ['id', 'user_one',
                           'user_two', 'relationship_start_date']
        for field in expected_fields:
            self.assertIn(field, data)

    def test_serializer_data_accuracy(self):
        """Test that serializer returns accurate data"""
        serializer = RelationshipSerializer(self.relationship)
        data = serializer.data

        self.assertEqual(data['user_one'], self.user1.id)
        self.assertEqual(data['user_two'], self.user2.id)
        self.assertEqual(data['relationship_start_date'], str(date.today()))


class RelationshipViewsTest(APITestCase):
    """Test Relationship views functionality"""

    def setUp(self):
        self.client = APIClient()
        self.user1 = Users.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='testpassword123',
            connection_code='USER01',
            first_name='User1',
            last_name='One'
        )
        self.user2 = Users.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='testpassword123',
            connection_code='USER02',
            first_name='User2',
            last_name='Two'
        )

    def test_manage_relationships_get_with_relationship(self):
        """Test GET manage_relationships when user has a relationship"""
        # Create a relationship
        Relationship.objects.create(
            user_one=self.user1,
            user_two=self.user2,
            relationship_start_date=date.today()
        )

        self.client.force_authenticate(user=self.user1)
        url = reverse('manage_relationship')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['user_one'], self.user1.id)
        self.assertEqual(response.data[0]['user_two'], self.user2.id)

    def test_manage_relationships_get_without_relationship(self):
        """Test GET manage_relationships when user has no relationship"""
        self.client.force_authenticate(user=self.user1)
        url = reverse('manage_relationship')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_create_relationship_request_valid(self):
        """Test creating a valid relationship request"""
        self.client.force_authenticate(user=self.user1)
        url = reverse('create_relationship_request')
        data = {'connection_code': 'USER02'}

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('has asked', response.data['message'])

        # Verify request was created
        request = RelationshipRequest.objects.get(
            requester=self.user1,
            receiver=self.user2
        )
        self.assertEqual(request.status, 'PENDING')

    def test_create_relationship_request_own_code(self):
        """Test creating relationship request with own connection code"""
        self.client.force_authenticate(user=self.user1)
        url = reverse('create_relationship_request')
        data = {'connection_code': 'USER01'}  # User's own code

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('other than your own', response.data['message'])

    def test_respond_relationship_request_accept(self):
        """Test accepting a relationship request"""
        # Create a request first
        request = RelationshipRequest.objects.create(
            requester=self.user1,
            receiver=self.user2,
            status='PENDING'
        )

        self.client.force_authenticate(user=self.user2)
        url = reverse('respond_relationship_request',
                      kwargs={'pk': request.id})
        data = {'accept': True}

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('are now dating', response.data['message'])

        # Verify relationship was created
        relationship = Relationship.objects.get(
            user_one=self.user1,
            user_two=self.user2
        )
        self.assertEqual(relationship.relationship_start_date, date.today())

    def test_respond_relationship_request_reject(self):
        """Test rejecting a relationship request"""
        # Create a request first
        request = RelationshipRequest.objects.create(
            requester=self.user1,
            receiver=self.user2,
            status='PENDING'
        )

        self.client.force_authenticate(user=self.user2)
        url = reverse('respond_relationship_request',
                      kwargs={'pk': request.id})
        data = {'accept': False}

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('has rejected', response.data['message'])

        # Verify request status was updated
        request.refresh_from_db()
        self.assertEqual(request.status, 'REJECTED')
