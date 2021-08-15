from django.test import TestCase
from django.contrib.auth import get_user_model

from unittest.mock import patch

from mainapp import models


def sample_user(email="test@gmail.com", password="Test1234"):
    """Creating a sample user to use them in tests"""
    return get_user_model().objects.create_user(email, password)


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

    # --------------------------Testing Tag Model-------------------------- #
    def test_tag_str(self):
        """Test whether tag comes in string representation"""
        tag = models.Tag.objects.create(
            user=sample_user(),
            name="Vegan"
        )
        # in Django models you can specify what field you want to use when you
        # convert a model to string representation (we chose name)
        self.assertEqual(str(tag), tag.name)

    # -----------------------Testing Ingredient Model----------------------- #
    def test_ingredient_str(self):
        """Test whether ingredient comes in string representation"""
        ingredient = models.Ingredient.objects.create(
            user=sample_user(),
            name="Tomato"
        )

        self.assertEqual(str(ingredient), ingredient.name)

    # -----------------------Testing Recipe Model----------------------- #
    def test_recipe_str(self):
        """Test whethter recipe comes in string representation"""
        recipe = models.Recipe.objects.create(
            user=sample_user(),
            title="Chicken with French Mushrooms",
            time_minutes=40,
            price=8.99
        )

        self.assertEqual(str(recipe), recipe.title)

    # -----------------------Testing Image Model----------------------- #
    @patch('uuid.uuid4')
    def test_recipe_file_name_uuid(self, mock_uuid):
        """Test that image is saved in correct locatin (with uuid)"""
        uuid = 'uuid-test'
        mock_uuid.return_value = uuid
    # when we call uuid func in patch, it will be triggered within our test
    # and test will override a default behavior, and will return just uuid var
        file_path = models.recipe_image_file_path(None, 'myimage.jpg')

        expected_file_path = f'uploads/recipe/{uuid}.jpg'

        self.assertEqual(file_path, expected_file_path)
