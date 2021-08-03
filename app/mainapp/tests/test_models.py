from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):
    def test_create_user_with_email(self):
        """"Checks wether the user was created with email successful"""

        email = "test@gmail.com"
        password = "Test1234"
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Check if all letters of an email are in lowercase"""
        email = "test@GOOGLE.COM"
        user = get_user_model().objects.create_user(email, "Test1234")

        self.assertEqual(user.email, email.lower())

    def test_user_invalid_email(self):
        """Test raising an error if the user put invalid email"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'Test1234')

    def test_create_superuser(self):
        """Test whether the superuser created successfully"""
        email = "test@gmail.com"
        password = "Test1234"
        user = get_user_model().objects.create_superuser(
            email=email,
            password=password
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
