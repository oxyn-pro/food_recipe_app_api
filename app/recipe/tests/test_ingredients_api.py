from django.contrib.auth import get_user_model
from django.urls import reverse

from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from mainapp.models import Ingredient

from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse("recipe:ingredient-list")


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicIngredientsApiTests(TestCase):
    """Test that any person/user can access ingredients API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        response = self.client.get(INGREDIENTS_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientApiTests(TestCase):
    """Test the authorized users can access ingredients API"""

    def setUp(self):
        self.user = create_user(email='testt@gmail.com', password='Test1234')

        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredient_list(self):
        """Test that authenticated user can retrieve a list of ingredients"""
        # sample ingredients
        Ingredient.objects.create(user=self.user, name='Potato')
        Ingredient.objects.create(user=self.user, name='Salt')

        response = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.all().order_by('-name')

        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data, serializer.data)

    def test_assigned_ingredients_limited_user(self):
        """Test if created ingredients by user assigned and limited only to
           that user"""
        user2 = create_user(email="testt2@gmail.com", password="Test12345")

        Ingredient.objects.create(user=user2, name='Kale')
        ingredient_orig_user = Ingredient.objects.create(user=self.user,
                                                         name='Honey')

        response = self.client.get(INGREDIENTS_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'],
                         ingredient_orig_user.name)

    def test_create_ingredient_successful(self):
        """Test creating a new ingredient"""
        payload = {'name': "Test ingredient"}

        # in order to create user must be already authenticated
        self.client.post(INGREDIENTS_URL, payload)

        exists = Ingredient.objects.filter(
            user=self.user,
            name=payload['name'],
        ).exists()

        self.assertTrue(exists)

    def test_create_ingredient_with_invalid_credentials(self):
        """Test creating ingredient with invalid credentials"""
        payload = {"name": ""}

        response = self.client.post(INGREDIENTS_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)