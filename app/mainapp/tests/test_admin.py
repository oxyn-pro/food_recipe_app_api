from django.test import TestCase, Client
# Client in order to be a test client to receive a request
from django.contrib.auth import get_user_model
# get_user_model in order to get a current active User model
from django.urls import reverse  # in order to generate a url/path


class TestAdminSite(TestCase):
    def setUp(self):
        """This is a setup function that runs before all test cases"""
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email='admin@gmail.com',
            password='admin1234'
        )

        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email="test@gmail.com",
            password="test1234",
            name="Test User"
        )

    def test_list_user(self):
        """Test whether users are listed
            in admin page or not"""
        url = reverse('admin:mainapp_customuser_changelist')
        response = self.client.get(url)

        self.assertContains(response, self.user.name)
        # It will check wether a user has name, email in a particular response
        self.assertContains(response, self.user.email)

    def test_user_change_page(self):
        """Test whether user edit page works or not"""
        # admin/mainapp/customuser/id/change
        url = reverse('admin:mainapp_customuser_change', args=[self.user.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    def test_user_add_page(self):
        """Test whether user add page works or not"""
        url = reverse("admin:mainapp_customuser_add")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
