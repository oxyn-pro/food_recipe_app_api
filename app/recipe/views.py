from rest_framework import viewsets, mixins
# mixins provide only create, list, retrieve operations of ViewSet
from rest_framework.authentication import TokenAuthentication
# token will be used in order to authenticate a user
from rest_framework.permissions import IsAuthenticated
# in order to use API endpoint user should authenticated

from . import serializers
from mainapp.models import Tag, Ingredient, Recipe


class BaseRecipeAttrsViewSet(viewsets.GenericViewSet,
                             mixins.ListModelMixin,
                             mixins.CreateModelMixin):
    """Common ViewSet attributes for both TagViewSet and IngredientViewSet
       classes. Manage tags, ingredients in the database, by listing,
       and controlling 'create' operations"""
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    # It means that, it will list items according to which ViewSet it is
    # referencing for. For example: .../tag/list/.. , .../ingredient/list/

    # ListModelMixin (aka list() from ViewSet) will call get_queryset to
    # retrieve objects/items from Tag.objects.all()
    def get_queryset(self):
        """Retrieve objects to current authenticated user"""
        return self.queryset.filter(user=self.request.user).order_by('-name')
        # request will have 'user' attached to it because
        # authentication_classes take care of authentication of user and
        # assignning it(user) to request. '.filter()' will filter by
        # currently authenticated user's name.
        # If 'request' came until this point, it means that user is already
        # authenticated because in order to come here first user should pass
        # through 'authentication_classes' and 'permission_classes'.
        # Here queryset is filtered, meaning that necessary ingredients will be
        # filtered / retrieved from ingredients by user's name.
        # ie. 'Kale = user1' is assigned to user1, 'Salt=user2' and etc.

    def perform_create(self, serializer):
        """Create a new tag/ingredient or any object that invokes
           this function"""
        serializer.save(user=self.request.user)
    # it will hook into 'create' process. When we do "create" function
    # in our ViewSet/CreateModelMixin 'perform_create' will be invoked,
    # and validated serializer(will be Dictionary data from Front,
    # like name=ingredientname) will do our modifications(such as saving
    # authenticated user into 'user')


class TagViewSet(BaseRecipeAttrsViewSet):
    """Manage tags in the database, by listing, and controlling
       create operations"""
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer


class IngredientViewSet(BaseRecipeAttrsViewSet):
    """Manage ingredients in the database, by listing, and controlling
       create operations"""
    queryset = Ingredient.objects.all()  # all objects assigned to the user
    serializer_class = serializers.IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """Manage recipes in the database, .create(), .retrieve(), .list(),
       .update(), .partial_update(), .destroy()"""

    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )
    queryset = Recipe.objects.all()
    serializer_class = serializers.RecipeSerializer

    def get_queryset(self):
        """Retrieve objects to current authenticated user"""
        return self.queryset.filter(user=self.request.user)

    # there are couple of actions available by default:
    # list = default return of list of objects in serializer,
    # retrieve = will retrieve other serializer and will use it
    # instead of first(default) called serializer (serializer_class)
    def get_serializer_class(self):
        """Return necessary serializer class when the default one
           needs to be overridden"""
        # self.action is the action that matches with the action of current
        # request
        if self.action == 'retrieve':
            return serializers.RecipeDetailSerializer
        return self.serializer_class
    # Of course we could create a new serializer and make serializer_class,
    # but it could be repetitive. That's why i just overrided the default
    # serializer with get_serializer_class()(new seraializer)

    def perform_create(self, serializer):
        """Create a new recipe process"""
        serializer.save(user=self.request.user)
