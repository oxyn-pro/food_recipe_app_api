from rest_framework import viewsets, mixins
# mixins provide only create, list, retrieve operations of ViewSet
from rest_framework.authentication import TokenAuthentication
# token will be used in order to authenticate a user
from rest_framework.permissions import IsAuthenticated
# in order to use API endpoint user should authenticated

from . import serializers
from .serializers import Tag


class TagViewSet(viewsets.GenericViewSet,
                 mixins.ListModelMixin,
                 mixins.CreateModelMixin):
    """Manage tags in the database, mainly listing"""
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
        # assignning it(user) to request.

    def perform_create(self, serializer):
        """Create a new tag"""
        serializer.save(user=self.request.user)
    # it will hook into 'create' process. When we do "create" function
    # in our ViewSet/CreateModelMixin 'perform_create' will be invoked,
    # and validated serializer(will be Dictionary data from Front,
    # like name= tagname) will do our modifications(such as saving
    # authenticated user into 'user')
