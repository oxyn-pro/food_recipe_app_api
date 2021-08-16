from django.contrib.auth import get_user_model
from django.urls import reverse

from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from mainapp.models import Ingredient, Recipe

from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse("recipe:ingredient-list")


# In order to filter by tags #--------------------

def create_sample_ingredient(user, name='Tomato'):
    return Ingredient.objects.create(user=user, name=name)


def create_sample_recipe(user, **params):
    default = {
        'title': 'Tomato Soup',
        'time_minutes': 45,
        'price': 4.55
    }

    default.update(params)
    return Recipe.objects.create(user=user, **default)

# In order to filter by tags #--------------------


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

    # -----------Test filtering by ingredients in ingredient side----------- #
    # .../ingredients/?recipe=3

    def test_retrieve_ingredients_assigned_to_recipes(self):
        """Filter by ingredients assigned to recipes"""
        ingredient1 = create_sample_ingredient(user=self.user, name='Corn')
        ingredient2 = create_sample_ingredient(user=self.user, name='Egg')

        recipe1 = create_sample_recipe(
            user=self.user,
            title='Corn Dog',
            time_minutes=15,
            price=5.20
        )

        recipe1.ingredients.add(ingredient1)

        response = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        serializer1 = IngredientSerializer(ingredient1)
        serializer2 = IngredientSerializer(ingredient2)

        self.assertIn(serializer1.data, response.data)
        self.assertNotIn(serializer2.data, response.data)

    def test_retrieve_ingredients_assigned_unique(self):
        """Filter ingredients by those are assigned to recipes returns
           unique items / ids of ingredients"""

        ingredient = create_sample_ingredient(user=self.user, name="Orange")
        create_sample_ingredient(user=self.user, name='Chocolate')

        recipe1 = create_sample_recipe(
            user=self.user,
            title="Orange Juice",
            time_minutes=10,
            price=6.00
        )

        recipe2 = create_sample_recipe(
            user=self.user,
            title="Orange Pie",
            time_minutes=40,
            price=20.00
        )

        recipe1.ingredients.add(ingredient)
        recipe2.ingredients.add(ingredient)

        response = self.client.get(INGREDIENTS_URL, {"assigned_only": 1})

        self.assertEqual(len(response.data), 1)
        # we will return 1, because we assigned only 1 id to two recipes
        # also here id is in int
