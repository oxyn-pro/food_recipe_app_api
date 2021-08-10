from django.contrib.auth import get_user_model, authenticate
# authenticate is the object that helps you auths the user if
# the valid credentials are passed

from django.utils.translation import ugettext_lazy as _
# it is recommended by django to include it whenever we want to output
# some text in our screen. If you add any other languages to your projects,
# you can add language file and this module will automatically convert it
# to correct language.


from rest_framework import serializers
# Serialazer helps to serialize the db and model objects to Python objects,
# and  to form them into JS, JSON objects. In a simple language it is
# responsible for converting objects into data types understandable by
# javascript and front-end frameworks.
# Also, there is the way to deserialize the JSON, JS objects into
# Python objects abd then to db objects.


class UserSerializer(serializers.ModelSerializer):
    """The Serializer for users object"""

    class Meta:
        model = get_user_model()  # gets a active User model(ie. 'CusromUser')
        fields = ('email', 'password', 'name')  # these are only fields that
        # we will accept, when the user is created.
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}
        # extra restrinctions,args to set for the fields that we reference in
        # "extra_kwargs"

        # fields will be included in serializer, meaning that they will be
        # converted to and from JSON when we make HTTP POST request.
        # After the POST request it will be retrieved from 'view', so we could
        # save it in our model.

    # this function overrides the original 'create' function.
    def create(self, validated_data):
        """Create a new user with encrypted data and return it"""
        return get_user_model().objects.create_user(**validated_data)
    # When the user is being created, after clicking 'submit' button,
    # the validated data about the user will come through HTTP POST to the
    # serializer (like: email, password, name (in "fields")) as a JSON format,
    # and that validated data we use in 'create' function, in order to pass it
    # to our 'create_user' function in our 'models'

    def update(self, instance, validated_data):
        """Update a user, setting password in correct form and return user"""
        # instance is linked into ModelSerializer class, meaning that it has
        # a reference to 'CustomUser'(user own) model, and it(class) can link
        # its(User mod)instances(objects of out model(in our case User model))
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()
        return user

# Front(JSON data) -> API -> HTTP POST -> Serializer -> create_user(models.py)


# Here we created a new serializer based on standard Django Serializer module
class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user authentication object
          (Token creation and its application)"""
    email = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    # it validates whether email, password are really CharField or not.
    # It also validates whether the authentication credentials are valid.
    def validate(self, attrs):  # attrs will be passed as a dictionary
        """Validate and authenticate the user"""
        email = attrs.get('email')  # these are attrs(atributes) that are
        password = attrs.get('password')  # passed to serializer(email, passw)

        # when a request is made, this serializer will be passed into viewset
        user = authenticate(  # then viewset will pass request's context into
            request=self.context.get('request'),  # this serializer.
            username=email,
            password=password
        )

        # if the authentication fails, meaning that it didn't return a user.
        if not user:
            msg = _('Unable to authenticate with provided credentials')
            # it will be outputted in the screen if authentication fails
            raise serializers.ValidationError(msg, code='authentication')

        attrs['user'] = user
        return attrs
