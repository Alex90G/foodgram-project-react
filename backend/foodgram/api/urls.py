from django.urls import include, path
from rest_framework import routers

from .views import (CustomUserViewSet, IngredientsViewSet, RecipesViewSet,
                    TagsViewSet)

router = routers.DefaultRouter()

router.register(r'users', CustomUserViewSet)
router.register(r'tags', TagsViewSet)
router.register(r'recipes', RecipesViewSet)
router.register(r'ingredients', IngredientsViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
