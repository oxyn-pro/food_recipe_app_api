from rest_framework import generics  # it will help us to pass the data
# through API to our database
from rest_framework import authentication, permissions

from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from user.serializers import UserSerializer, AuthTokenSerializer


# it will make an API to create objects in database
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


# 'authentication' is a mechanism by which authentication happens,
# it can be through cookie(CookieAuthentication), token(TokenAuthentication)..
class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user(modefying user's email, and etc.)"""
    serializer_class = UserSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    # the level of access that user has

    # this func will get the model (table in most cases) for logged in users,
    # and 'return' will return an item of the model (in our case 'user')
    def get_object(self):
        """Retrieve a user from a model(we do not mention it in code
           but which in our case is model of logged in users) and return it"""
        return self.request.user
        # request will have 'user' attached to it because
        # authentication_classes take care of authentication of user and
        # assignning it(user) to request.
