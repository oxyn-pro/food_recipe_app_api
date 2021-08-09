from rest_framework import generics  # it will help us to pass the data
# through API to our database

from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from user.serializers import UserSerializer, AuthTokenSerializer


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system (it will create objects in db)"""
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """Create a new authentication token for user"""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
    # this will basically sets a render so we can view the endpoint
    # in the browser. If we want to use other class to render we
    # can just type it and it will be automatically changed in views.
    # Except renderer we can use C URL tool.
