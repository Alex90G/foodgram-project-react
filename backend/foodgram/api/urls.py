from django.urls import include, path
from rest_framework import routers

from .views import IngredientsViewSet, RecipesViewSet, TagsViewSet

router_v1 = routers.DefaultRouter()

router_v1.register(r'tags', TagsViewSet)
router_v1.register(r'recipes', RecipesViewSet)
router_v1.register(r'ingredients', IngredientsViewSet)

urlpatterns = [
    path('', include(router_v1.urls)),
]
