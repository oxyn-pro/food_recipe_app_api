from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from mainapp.models import Recipe, Tag, Ingredient

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer


RECIPES_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    """Return recipe detail URL"""
    return reverse("recipe:recipe-detail", args=[recipe_id])
    # it will look like this: .../recipe/recipes/1


def create_user(**params):
    return get_user_model().objects.create_user(**params)


# in tests we can create our own recipes by just overriding default vals
def create_sample_recipe(user, **params):
    """Create and retrieve a sample recipe"""
    defaults = {
        "title": "Sample recipe",
        "time_minutes": 10,
        "price": 5.99
    }
    defaults.update(params)
    # here we can assign any params to this function and it will by default
    # update those values which are in defaults or it(defaults) will
    # create/accept other params and save dictionary.

    return Recipe.objects.create(user=user, **defaults)


def create_sample_tag(user, name="Lunch"):
    """Create and retrieve a sample tag"""
    return Tag.objects.create(user=user, name=name)


def create_sample_ingredient(user, name="Sugar"):
    """Create and retrieve a sample ingredient"""
    return Ingredient.objects.create(user=user, name=name)


class PublicRecipesApiTests(TestCase):
    """Test publicly available ingredients API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test login is required for retrieving ingredients"""
        response = self.client.get(RECIPES_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipesApiTests(TestCase):
    """Test the authorized user ingredients"""

    def setUp(self):
        self.user = create_user(email="testt@gmail.com", password="Test1234")
        self.client = APIClient()

        self.client.force_authenticate(self.user)

    def test_retrieve_recipe_list(self):
        """Test if authenticated users can retrieve/see ingredients that
           he/she created"""

        create_sample_recipe(user=self.user)
        create_sample_recipe(user=self.user)

        response = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all()  # .order_by("-id")
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

        # here the var serializer refers to RecipeSerializer, meaning that
        # it will show the data that is stored in table in database.
        # ie. >>> print(repr(serializer))
        # RecipeSerializer():
        #   id = IntegerField(label='ID', read_only=True)
        #   title = CharField(max_length=255)
        #   ingredients = PrimaryKeyRelatedField(
        #                 queryset=Ingredient.objects.all())
        #   ...

    def test_assigned_recipes_limited_user(self):
        """Test if the authenticated(logged in) user gets only
           assigned recipes to his/her user. Or with other words,
           recipes returned are for the current authencticated user"""

        user2 = create_user(email='testt2@gmail.com', password='Test12345')

        create_sample_recipe(user=user2)
        create_sample_recipe(user=self.user)

        response = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data, serializer.data)

    def test_view_recipe_detail(self):
        """Test viewing recipe detail (accessing that endpoint)"""
        recipe = create_sample_recipe(user=self.user)

        # After defining the Many to many relationship of models
        # (Tag, Ingredient, Recipe) in serializer and models, we can now
        # add tags, ingredients like this:
        recipe.tags.add(create_sample_tag(user=self.user))
        recipe.ingredients.add(create_sample_ingredient(user=self.user))
        # here, we are adding tag and ingredient to current created recipe

        url = detail_url(recipe.id)
        response = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(response.data, serializer.data)

    # -----Testing Creating Recipes(with and without tags, ingredients)----- #
    def test_create_basic_recipe(self):
        """Test creating basic recipe"""
        payload = {
            'title': 'Chocolate pie',
            'time_minutes': 15,
            'price': 6.00
        }

        response = self.client.post(RECIPES_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # when you create an object in django rest framework, the dictionary
        # containing the created object will be returned back.
        recipe = Recipe.objects.get(id=response.data['id'])  # id ofcreated ob
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))
            # getattr = recipe[title] / recipe[time_minutes] / recipe[price]

    def test_create_recipe_with_tags(self):
        """Test creating recipe with tags assigned to it"""
        # the way of assigning tags is to pass in a list of tag ids when you
        # create a recipe
        tag1 = create_sample_tag(user=self.user, name='Fruit')
        tag2 = create_sample_tag(user=self.user, name='Dessert')

        payload = {
            'title': 'Apples cake',
            'tags': [tag1.id, tag2.id],
            'time_minutes': 45,
            'price': 15.00,
        }

        response = self.client.post(RECIPES_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=response.data['id'])
        tags = recipe.tags.all()  # will retrieve all tags in recipe and
        # it will be in queryset: tag1, tag2, ... all of this without in list

        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_recipe_with_ingredients(self):
        """Test creating recipe with ingredients"""
        ingredient1 = create_sample_ingredient(user=self.user, name='Tomato')
        ingredient2 = create_sample_ingredient(user=self.user, name='Eggs')

        payload = {
            'title': 'Tomato Omelette',
            'ingredients': [ingredient1.id, ingredient2.id],
            'time_minutes': 25,
            'price': 2.99
        }

        response = self.client.post(RECIPES_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=response.data['id'])

        ingredients = recipe.ingredients.all()

        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)

    # -------Testing Updating Recipe(partials update and full update)------- #
    # 'update' is already inserted in ModelViewSet(views), that's why we don't
    # need to implement it manually in views(ViewSet). (So all tests pass)
    def test_partial_update_recipe(self):
        """Test updating a recipe with patch(partial update)"""
        recipe = create_sample_recipe(user=self.user)
        recipe.tags.add(create_sample_tag(user=self.user))
        new_tag = create_sample_tag(user=self.user, name='Fish')

        payload = {'title': 'Fish in Mangal', 'tags': [new_tag.id]}
        url = detail_url(recipe.id)
        self.client.patch(url, payload)

        recipe.refresh_from_db()
        tags = recipe.tags.all()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(len(tags), 1)
        self.assertIn(new_tag, tags)

    def test_full_update_recipe(self):
        """Test updating a recipe with put(full update)"""
        recipe = create_sample_recipe(user=self.user)
        recipe.tags.add(create_sample_tag(user=self.user))

        payload = {
            'title': 'Potato with Mayo',
            'time_minutes': 15,
            'price': 2.00
        }

        url = detail_url(recipe.id)
        self.client.put(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.time_minutes, payload['time_minutes'])
        self.assertEqual(recipe.price, payload['price'])
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 0)
