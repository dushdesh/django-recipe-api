from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
USER_TOKEN_URL = reverse('user:token')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test the users API (public)"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test creating a valid user is successful"""
        payload = {
            'email': 'rinkidink@test.com',
            'password': 'rinkidinkstinks',
            'name': 'TestRink',
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)

        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_create_user_exists_failure(self):
        """Creating user that already exists fails"""
        payload = {
            'email': 'lorem@impsum.com',
            'password': 'loremipsumdolor',
            'name': 'Test'
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test password must be more then 4 chars"""
        payload = {
            'email': 'lorem@impsum.com',
            'password': 'lore',
            'name': 'Test'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()

        self.assertFalse(user_exists)

    def test_create_user_token(self):
        """Test that a token is created for the user"""
        payload = {
            'email': 'lorem@impsum.com',
            'password': 'loremipsum'
        }
        create_user(**payload)
        res = self.client.post(USER_TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_creds(self):
        """Test token is not created with invalid creds"""
        create_user(email='lorem@impsum.com', password='loremipsum')
        payload = {
            'email': 'lorem@impsum.com',
            'password': 'wrongpassword'
        }
        res = self.client.post(USER_TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_with_user_not_created(self):
        """Token not created if user does not exists"""
        payload = {
            'email': 'lorem@impsum.com',
            'password': 'loremipsum'
        }
        res = self.client.post(USER_TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field_password(self):
        """Test password is required to issue token"""
        res = self.client.post(
            USER_TOKEN_URL,
            {
                'email': 'some',
                'password': ''
            }
        )

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field_email(self):
        """Test email is required to issue token"""
        res = self.client.post(
            USER_TOKEN_URL,
            {
                'email': '',
                'password': 'loremipsum',
            }
        )

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
