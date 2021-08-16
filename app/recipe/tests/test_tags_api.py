from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from mainapp.models import Tag, Recipe

from recipe.serializers import TagSerializer


TAGS_URL = reverse('recipe:tag-list')


# In order to filter by tags #--------------------

def create_sample_tag(user, name='Fresh'):
    return Tag.objects.create(user=user, name=name)


def create_sample_recipe(user, **params):
    defaults = {
        'title': 'Sample Recipe',
        'time_minutes': 15,
        'price': 10.00
    }
    defaults.update(params)

    return Recipe.objects.create(user=user, **defaults)

# In order to filter by tags #--------------------


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicTagsApiTests(TestCase):
    """Test the publicly available tags API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retrieving tags"""
        response = self.client.get(TAGS_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """Test the authorized user tags API"""

    def setUp(self):
        self.user = create_user(email='testt@gmail.coom', password='Test1234')

        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tag_list(self):
        """Test if an authenticated user can see/retrieve tags
           that he/she created"""

        Tag.objects.create(user=self.user, name="Vegan")
        # an authenticated user created a tag
        Tag.objects.create(user=self.user, name="Dessert")

        response = self.client.get(TAGS_URL)

        # By this we are retrieving all tags of our user from our database
        tags = Tag.objects.all().order_by('-name')

        # Serializer will take items from database and
        # deserialize(transforms database object type) to JSON
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # As our response data and Serializer data are both in JSON format
        # we want to check it
        self.assertEqual(response.data, serializer.data)

    def test_assigned_tags_limited_user(self):
        """Test if the authenticated(logged in) user gets only
           assigned tags to his/her user. Or with other words, tags
           returned are for the authenticated user"""

        user2 = create_user(email="testt2@gmail.com", password="Test12345")

        Tag.objects.create(user=user2, name="Fruit")
        tag_orig_user = Tag.objects.create(user=self.user, name="Sweet")

        response = self.client.get(TAGS_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], tag_orig_user.name)

    # test with authenticated user
    def test_create_tag_successful(self):
        """Test creating a new tag"""
        # in order to create user must be already authenticated
        payload = {"name": "Testtag"}
        self.client.post(TAGS_URL, payload)

        exists = Tag.objects.filter(
            user=self.user,
            name=payload["name"]
        ).exists()

        self.assertTrue(exists)

    def test_tag_with_invalid_credentials(self):
        """Test create tag to raise error if invalid credentials are passed"""
        payload = {"name": ""}
        response = self.client.post(TAGS_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ------------------------Test filtering by tags------------------------ #
    # ie. .../tags/?recipe=2

    def test_retrieve_tags_assigned_to_recipes(self):
        "Filtering tags by those that are assigned to recipes"
        tag1 = create_sample_tag(user=self.user, name='Vegan')
        tag2 = create_sample_tag(user=self.user, name='Fast Food')

        recipe = create_sample_recipe(
            user=self.user,
            title="Basile Salat",
            time_minutes=15,
            price=10.00
        )
        recipe.tags.add(tag1)

        response = self.client.get(TAGS_URL, {"assigned_only": 1})
        # will filter by tags that are assigned only (to recipes)
        # 1 means True, 0 means False(default)

        serializer1 = TagSerializer(tag1)
        serializer2 = TagSerializer(tag2)

        self.assertIn(serializer1.data, response.data)
        self.assertNotIn(serializer2.data, response.data)

    def test_retrieve_tags_assigned_unique(self):
        """Filtering tags by those are assigned to recipes returns
           unique items / ids of tags"""
        tag = create_sample_tag(user=self.user, name='Japanese culture')
        create_sample_tag(user=self.user, name='Indian Spices')

        recipe1 = create_sample_recipe(
            user=self.user,
            title='Sushi with tuna',
            time_minutes=10,
            price=15.00
        )

        recipe2 = create_sample_recipe(
            user=self.user,
            title='Fried octopus with soy souce',
            time_minutes=25,
            price=10.00
        )

        recipe1.tags.add(tag)
        recipe2.tags.add(tag)

        response = self.client.get(TAGS_URL, {'assigned_only': 1})

        self.assertEqual(len(response.data), 1)
        # we will return 1, because we assigned only 1 id to two recipes
        # also here id is in int
