from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):
    email = "test@dushdesh@hotmail.com"
    password = "test123"

    def test_create_user_with_email_successful(self):
        # Test creating a new user with an email is successful
        user = get_user_model().objects.create_user(self.email, self.password)
        self.assertEqual(user.email, self.email)
        self.assertTrue(user.check_password(self.password))

    def test_new_user_email_normalized(self):
        # Test the email for a user is normalized
        email = 'test@DUSHDESH.COM'
        user = get_user_model().objects.create_user(email, self.password)
        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        # Test creating user without email raises error
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, self.password)

    def test_create_new_superuser(self):
        # Test creating a super user
        user = get_user_model().objects.create_superuser(
            self.email,
            self.password
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
