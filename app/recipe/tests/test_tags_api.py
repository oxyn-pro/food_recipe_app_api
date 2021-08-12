from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from mainapp.models import Tag

from recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')


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

    def test_retrieve_tags(self):
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
