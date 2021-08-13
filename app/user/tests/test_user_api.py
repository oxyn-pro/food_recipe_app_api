from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
# Test client to make test requests to our API and check the response
from rest_framework import status
# status codes that contains response in readable form

CREATE_USER_URL = reverse("user:create")
# assigns create user url to create_user_url var

TOKEN_URL = reverse("user:token")
# This is the url tha we will make a HTTP POST request to generate a token

ME_URL = reverse("user:me")
# this will store the url that will allow a user to modefy his/her account


def create_user(**params):  # this function is to make other function shorter
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test the users API (public). Public: when anyone from the internet
       can access that API (example: create user). Private: when only
       authenticated users can perform an action (example: modefy a user,
       change a user password and etc."""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_successfully(self):
        """Test creating a user with valid payload is successful.
           Check whether a user is created successfully or not.
           Payload is an object that you pass to API when making a request"""

        payload = {
            "email": "test@gmail.com",
            "password": "Test1234",
            "name": "Test Name"
        }
        response = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # From here we just want to be sure, whether a user is created or not
        user = get_user_model().objects.get(**response.data)
        # API and HTTP post method return response of its values after
        # successful attempt and now we are taking it and assigning it to user
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn("password", response.data)

    def test_user_exists(self):
        """Test creating user that already exists, if it exists
           fails / raise an error"""

        payload = {
            "email": "test@gmail.com",
            "password": "Test1234",
            "name": "Test"
        }
        create_user(**payload)

        response = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test that checks a password contains at least 5 chars,
           otherwise raise an error """

        payload = {
            "email": "test@gmail.com",
            "password": "qs",
            "name": "Test"
        }
        response = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    # ----------------------TEST TOKEN AUTH FIELD--------------------------- #
    def test_create_token_for_user(self):
        """Test if the token was successfully created for the user"""
        payload = {
            "email": "test2gmail.com",
            "password": "Test1234"
        }
        create_user(**payload)

        # Here, we are generating token to a created user(by passing payload)
        response = self.client.post(TOKEN_URL, payload)
        self.assertIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # And we are checking that there is token in our HTTP POST response
        # If there is token HTTP 200 OK should be sent back in in our response

    def test_create_token_for_invalid_credentials(self):
        """Test, a token is not created if invalid credentials is provided"""
        create_user(email="test@gmail.com", password="Test1234")
        # Here we first create a user, in order to deliberatly pass
        # wrong password in payload to the HTTP POST request of token creation

        payload = {
            "email": "test@gmail.com",
            "password": "wrong"
        }

        # If invalid credentials are provided, the token must not be included
        # in response and raise an error
        response = self.client.post(TOKEN_URL, payload)
        self.assertNotIn("token", response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_not_existed_user(self):
        """Test that token isn't created if a user does not exist in system"""
        payload = {
            "email": "test@gmail.com",
            "password": "Test1234"
        }

        # we are trying to generate token for not created user
        response = self.client.post(TOKEN_URL, payload)
        self.assertNotIn("token", response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """Test that token is not generated if there are missing fields
           like email, password, and etc."""
        create_user(email="test@gmail.com", password="Test1234")

        payload = {
            "email": "test@gmail.com",
            "password": ""
        }

        # we will send empty password(field) in order to check errors
        response = self.client.post(TOKEN_URL, payload)
        self.assertNotIn("token", response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # -------MAKE SURE THAT USER IS AUTHORIZED TO ACCESS 'me' ENDPOINT------ #
    def test_auth_required_to_modefy(self):
        """Test that an authentication is required for a user
           in order to modefy his/her own user's data"""
        response = self.client.get(ME_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Authentication is required in order to use these related endpoints"""
# -----FORSE AUTHORIZE 'user' AND TEST IF THE RESPONSE HAS RELEVANT DATA---- #
    def setUp(self):
        self.user = create_user(
            email='testt@gmail.com',
            password='test1234',
            name="test"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)  # oneuser for alltests
        # By these, every time when each of our
        # tests run we will make sure that a user is authenticated

    def test_retrieving_logged_in_user(self):
        """Test logged in user is retrieved successfully"""

        response = self.client.get(ME_URL)

        # after successfully logging in, then check status_code and whether
        # data from response of HTTP GET is equal to the actual user's data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            'name': self.user.name,  # test
            'email': self.user.email,  # testt@gmail.co
        })

    def test_post_not_allowed_me_url(self):
        """Test that HTTP POST method is not allowed on 'me' url,
           we what updata data using API"""

        response = self.client.post(ME_URL, {})

        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    # authenticated user can update his/her profile, not ordinary users
    def test_update_user_profile(self):
        """Test update user profile for authenticated user"""

        payload = {
            "name": "new test",
            "password": "newtest1234"
        }
        # patch will change the matching user data in our case (name, passw)
        response = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
