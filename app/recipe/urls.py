from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('tags', views.TagViewSet)  # .../tags/...
# for example: user/tags/
#              user/tags/1
#              user/tags/1(change)
# those all changes(create, list, retrieve)'s urls are dynamically added

router.register('ingredients', views.IngredientViewSet)
router.register('recipes', views.RecipeViewSet)

app_name = 'recipe'

urlpatterns = [
    path('', include(router.urls))
]
