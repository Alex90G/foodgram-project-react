from django.db.models import Sum
from django.http import FileResponse
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import (FavoriteRecipes, Ingredients,
                            IngredientsForRecipes, Recipes, ShoppingCart, Tags)
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .filters import IngredientsFilters, RecipesFilters
from .mixins import CustomRecipeViewSet, ListRetrieveViewSet
from .pagination import CustomPageNumberPagination
from .permissions import AuthorAdminOrReadOnly
from .serializers import (FavoriteRecipesSerializer, IngredientsSerializer,
                          RecipesSerializer, ShoppingCartSerializer,
                          TagsSerializer)


class TagsViewSet(ListRetrieveViewSet):
    """Обрабатывает запросы по тегам."""
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    permission_classes = (permissions.AllowAny,)


class IngredientsViewSet(ListRetrieveViewSet):
    """Обрабатывает запросы по ингредиентам."""
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    permission_classes = (permissions.AllowAny,)
    filter_backends = (IngredientsFilters,)
    search_fields = ('^name',)


class RecipesViewSet(CustomRecipeViewSet):
    """
    Обрабатывает запосы по рецептам.
    Добавлены методы для добавления рецепта в избранное,
    в ксписок покупок и выгрузка списка покупок.
    """
    queryset = Recipes.objects.all()
    serializer_class = RecipesSerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = (DjangoFilterBackend, )
    filter_class = RecipesFilters
    permission_classes = (AuthorAdminOrReadOnly,)

    @action(
        detail=True, methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def favorite(self, request, pk=None):
        if request.method == 'POST':
            return self.adding_object(model=FavoriteRecipes,
                                      pk=pk,
                                      serializers=FavoriteRecipesSerializer,
                                      user=request.user)
        if request.method == 'DELETE':
            return self.deleting_object(
                model=FavoriteRecipes, pk=pk, user=request.user
            )
        return None

    @action(
        detail=True, methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def shopping_cart(self, request, pk=None):
        if request.method == 'POST':
            return self.adding_object(model=ShoppingCart,
                                      pk=pk,
                                      serializers=ShoppingCartSerializer,
                                      user=request.user)
        if request.method == 'DELETE':
            return self.deleting_object(
                model=ShoppingCart, pk=pk, user=request.user
            )
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(detail=False, permission_classes=[permissions.IsAuthenticated])
    def download_shopping_cart(self, request):
        user = request.user
        shopping_list = 'Список покупок:\n '
        ingredients = IngredientsForRecipes.objects.filter(
            recipes__shopping_cart__user=user).values(
                'ingredients__name',
                'ingredients__measurement_unit').order_by(
                    'ingredients__name').annotate(amount=Sum('amount'))
        for ingredient in ingredients:
            shopping_list = (
                f"{shopping_list}\n" + f"{ingredient['ingredients__name']} "
                + " -"
                f" {ingredient['amount']} "
                f"{ingredient['ingredients__measurement_unit']}; "
            )

        return FileResponse(
            shopping_list, as_attachment=True, filename='ShoppingList.txt',
            content_type='text/plain;charset=UTF-8'
        )
