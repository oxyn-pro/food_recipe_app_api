from rest_framework import serializers
from mainapp.models import Tag, Ingredient, Recipe


# here Serializer looks into Tag model, and retrieves data from database,
# in order to serialize to the front.
class TagSerializer(serializers.ModelSerializer):
    """Serializer for tag objects"""

    class Meta:
        model = Tag
        fields = ('id', 'name')
        read_only_fields = ('id',)
        # we addded id as read only field, because we want to prevent user
        # of updating the id of the objects, it means they can update other
        # fields mentioned in 'fields'.


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for ingredient objects"""

    class Meta:
        model = Ingredient
        fields = ('id', 'name')
        read_only_fields = ('id',)


class RecipeSerializer(serializers.ModelSerializer):
    """Serialize a recipe"""

    # in order to connect many to many relation of tables,
    # we need to first retrieve Primary Key field of that table,
    # meaning that we will pass only PK, in our case it is 'id'.
    # Then the list of ids of ingredients will be accessed by serializer
    # of main model (ie. 'Recipe' model).
    ingredients = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Ingredient.objects.all()
    )

    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )

    class Meta:
        model = Recipe
        fields = (
            'id', 'title', 'ingredients', 'tags', 'time_minutes',
            'price', 'link'
        )
        read_only_fields = ('id', )


# here we will base our class from RecipeSerializer
# if more than one model was given, then in order to get all the mentioned
# models in one (like a recipe), we need to add all these serializers together
# into one common one. Those. we need to get detailed information about
# a specific recipe, then we need all the information about tags, ingredients,
# and to get it we need to combine all serializers together.
class RecipeDetailSerializer(RecipeSerializer):
    """Serialize a recipe detail"""

    # we can nest serializers
    ingredients = IngredientSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)


class RecipeImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading images to recipes"""

    class Meta:
        model = Recipe
        fields = ('id', 'image')
        read_only_fields = ('id',)
