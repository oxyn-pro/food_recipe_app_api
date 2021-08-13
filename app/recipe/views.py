from rest_framework import viewsets, mixins
# mixins provide only create, list, retrieve operations of ViewSet
from rest_framework.authentication import TokenAuthentication
# token will be used in order to authenticate a user
from rest_framework.permissions import IsAuthenticated
# in order to use API endpoint user should authenticated

from . import serializers
from mainapp.models import Tag, Ingredient


class TagViewSet(viewsets.GenericViewSet,
                 mixins.ListModelMixin,
                 mixins.CreateModelMixin):
    """Manage tags in the database, by listing, and controlling
       create operations"""
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer

    # ListModelMixin (aka list() from ViewSet) will call get_queryset to
    # retrieve objects/items from Tag.objects.all()
    def get_queryset(self):
        """Return objects(tags) for current authenticated user"""
        return self.queryset.filter(user=self.request.user).order_by('-name')
        # request will have 'user' attached to it because
        # authentication_classes take care of authentication of user and
        # assignning it(user) to request. '.filter()' will filter by
        # currently authenticated user's name.
        # If 'request' came until this point, it means that user is already
        # authenticated because in order to come here first user should pass
        # through 'authentication_classes' and 'permission_classes'.

    def perform_create(self, serializer):
        """Create a new tag"""
        serializer.save(user=self.request.user)
    # it will hook into 'create' process. When we do "create" function
    # in our ViewSet/CreateModelMixin 'perform_create' will be invoked,
    # and validated serializer(will be Dictionary data from Front,
    # like name= tagname) will do our modifications(such as saving
    # authenticated user into 'user')


class IngredientViewSet(viewsets.GenericViewSet,
                        mixins.ListModelMixin,
                        mixins.CreateModelMixin):
    """Manage ingredients in the database, by listing, and controlling
       create operations"""
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )
    queryset = Ingredient.objects.all()  # all objects assigned to the user
    serializer_class = serializers.IngredientSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by('-name')
        # here queryset is filtered, meaning that necessary ingredients will be
        # filtered / retrieved from ingredients by user's name.
        # ie. 'Kale = user1' is assigned to user1, 'Salt=user2' and etc.

    def perform_create(self, serializer):
        """Create a new ingredient"""
        serializer.save(user=self.request.user)
    # it will hook into 'create' process. When we do "create" function
    # in our ViewSet/CreateModelMixin 'perform_create' will be invoked,
    # and validated serializer(will be Dictionary data from Front,
    # like name=ingredientname) will do our modifications(such as saving
    # authenticated user into 'user')
