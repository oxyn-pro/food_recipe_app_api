from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, mixins, status
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

    # helper function
    def _params_str_to_ints(self, qs):
        """Convert a list of string IDs to a list of integers"""
        return list(map(int, qs.split(',')))
        # It is the same as [int(str_id) for str_id in qs.split(',')]

    # overridden function
    def get_queryset(self):
        """Retrieve objects to current authenticated user"""
        tags = self.request.query_params.get('tags')
        ingredients = self.request.query_params.get('ingredients')
        queryset = self.queryset
        if tags:
            tag_ids = self._params_str_to_ints(tags)
            queryset = queryset.filter(tags__id__in=tag_ids)
            # tags in recipe queryset, it has a foreign key to tags table
            # that has id collumn, double underscores __id__ mean
            # filter in a remote table, and in means return all tags that
            # match to the list of tags  that we provide (ie. tags).
        if ingredients:
            ingredient_ids = self._params_str_to_ints(ingredients)
            queryset = queryset.filter(ingredients__id__in=ingredient_ids)
    # dictionary containing all of query params that are provided in request
    # ie. [tags, ingredients, ...] => these are all queries that contain objcs
        return queryset.filter(user=self.request.user)

    # overridden function.
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
        elif self.action == 'upload_image':
            return serializers.RecipeImageSerializer
        return self.serializer_class
    # Of course we could create a new serializer and make serializer_class,
    # but it could be repetitive. That's why i just overrided the default
    # serializer with get_serializer_class()(new seraializer)

    # overridden function
    def perform_create(self, serializer):
        """Create a new recipe process"""
        serializer.save(user=self.request.user)

    # created own function / helper function
    # create custom action to post image to recipe. detail means that
    # we can upload images only to created recipes(through recipe detail),
    # it will use detail URL that has ID in it.
    # Upload image is the path/name of url: .../recipes/1/upload-image
    @action(methods=["POST"], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):  # pk(aka id) passed through url
        """Upload an image to a recipe"""
        recipe = self.get_object()
        # it will get recipe's object trough id that was included in URL

        serializer = self.get_serializer(  # retrieves it own
            recipe,                        # serializer(RecipeImageSerializer)
            data=request.data
        )

        if serializer.is_valid():  # it makes sure that all data correct
            serializer.save()      # like image field correct
            return Response(
                serializer.data,  # id of recipe, Url of the image
                status=status.HTTP_200_OK
            )
        # As there is ModelSerializer in our RecipeImageSerializer, we can
        # .save() data in our model, with updated data(fields).
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
