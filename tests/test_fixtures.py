"""
Test fixtures and sample data for the MCDA API project.
"""
from datetime import date, timedelta

from Account.models import Users
from Privacy.models import UserPrivacy
from Relationships.models import Relationship, RelationshipRequest


class TestDataFactory:
    """Factory class for creating test data"""

    @staticmethod
    def create_sample_user(username="sampleuser", email="sample@example.com",
                           password="samplepass123", **kwargs):
        """Create a sample user with all fields populated"""
        defaults = {
            'first_name': 'Sample',
            'last_name': 'User',
            'gender': 'CISMALE',
            'sexuality': 'HETEROSEXUAL',
            'connection_code': f"SMPL{username[-2:].upper()}",
            'has_accepted_terms_and_conditions': True,
            'has_accepted_privacy_policy': True,
        }
        defaults.update(kwargs)

        return Users.objects.create_user(
            username=username,
            email=email,
            password=password,
            **defaults
        )

    @staticmethod
    def create_couple():
        """Create a couple of users for relationship testing"""
        user1 = TestDataFactory.create_sample_user(
            username="alice",
            email="alice@example.com",
            first_name="Alice",
            last_name="Smith",
            gender="CISFEMALE",
            sexuality="HETEROSEXUAL",
            connection_code="ALICE1"
        )

        user2 = TestDataFactory.create_sample_user(
            username="bob",
            email="bob@example.com",
            first_name="Bob",
            last_name="Johnson",
            gender="CISMALE",
            sexuality="HETEROSEXUAL",
            connection_code="BOB001"
        )

        return user1, user2

    @staticmethod
    def create_relationship(user1, user2, start_date=None):
        """Create a relationship between two users"""
        if start_date is None:
            start_date = date.today() - timedelta(days=30)

        return Relationship.objects.create(
            user_one=user1,
            user_two=user2,
            relationship_start_date=start_date
        )

    @staticmethod
    def create_relationship_request(requester, receiver, status='PENDING'):
        """Create a relationship request"""
        return RelationshipRequest.objects.create(
            requester=requester,
            receiver=receiver,
            status=status
        )

    @staticmethod
    def create_privacy_settings(user, allow_status=True, allow_last_seen=True):
        """Create privacy settings for a user"""
        return UserPrivacy.objects.create(
            user=user,
            allow_status_visibility=allow_status,
            allow_last_seen=allow_last_seen
        )

    @staticmethod
    def create_test_scenario_love_triangle():
        """Create a love triangle scenario for complex testing"""
        # Create three users
        alice = TestDataFactory.create_sample_user(
            username="alice",
            email="alice@example.com",
            first_name="Alice",
            connection_code="ALICE1"
        )

        bob = TestDataFactory.create_sample_user(
            username="bob",
            email="bob@example.com",
            first_name="Bob",
            connection_code="BOB001"
        )

        charlie = TestDataFactory.create_sample_user(
            username="charlie",
            email="charlie@example.com",
            first_name="Charlie",
            connection_code="CHAR01"
        )

        # Alice and Bob are together
        relationship = TestDataFactory.create_relationship(alice, bob)

        # Charlie wants Alice (pending request)
        request = TestDataFactory.create_relationship_request(charlie, alice)

        # Create privacy settings for all
        TestDataFactory.create_privacy_settings(alice)
        TestDataFactory.create_privacy_settings(bob, allow_status=False)
        TestDataFactory.create_privacy_settings(charlie, allow_last_seen=False)

        return {
            'users': {'alice': alice, 'bob': bob, 'charlie': charlie},
            'relationship': relationship,
            'request': request
        }


# Sample data sets for different test scenarios
SAMPLE_USER_DATA = {
    'valid_registration': {
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john.doe@example.com',
        'username': 'johndoe',
        'password1': 'securepassword123',
        'password2': 'securepassword123',
        'gender': 'CISMALE',
        'sexuality': 'HETEROSEXUAL',
        'has_accepted_terms_and_conditions': True,
        'has_accepted_privacy_policy': True
    },

    'invalid_registration_password_mismatch': {
        'first_name': 'Jane',
        'last_name': 'Smith',
        'email': 'jane.smith@example.com',
        'username': 'janesmith',
        'password1': 'password123',
        'password2': 'differentpassword',
        'gender': 'CISFEMALE',
        'sexuality': 'BISEXUAL',
        'has_accepted_terms_and_conditions': True,
        'has_accepted_privacy_policy': True
    },

    'minimal_registration': {
        'first_name': 'Min',
        'last_name': 'User',
        'email': 'min@example.com',
        'username': 'minuser',
        'password1': 'minpass123',
        'password2': 'minpass123',
        'has_accepted_terms_and_conditions': True,
        'has_accepted_privacy_policy': True
    }
}

GENDER_CHOICES_TEST_DATA = [
    'CISMALE', 'CISFEMALE', 'TRANSMALE', 'TRANSFEMALE',
    'NONBINARY', 'INTERSEX', 'AGENDER', 'OTHER', 'PREFERNOTTOSAY'
]

SEXUALITY_CHOICES_TEST_DATA = [
    'HETEROSEXUAL', 'HOMOSEXUAL', 'BISEXUAL', 'ASEXUAL',
    'PANSEXUAL', 'DEMISEXUAL', 'POLYSEXUAL', 'OTHER', 'PREFERNOTTOSAY'
]

RELATIONSHIP_STATUS_TEST_DATA = [
    'ACCEPTED', 'PENDING', 'REJECTED', 'BLOCKED'
]
