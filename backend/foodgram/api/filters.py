from django_filters.rest_framework import FilterSet, filters
from recipes.models import Recipes, Tags
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from users.models import User


class RecipesFilters(FilterSet):
    """
    Фильтрации рецептов:
    1) по тегам
    2) по автору
    3) по вхождению рецепта в число избранных рецептов
    4) по вхождению рецепта в список покупок.
    """
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        queryset=Tags.objects.all(),
        to_field_name='slug'
    )
    author = filters.ModelChoiceFilter(
        queryset=User.objects.all()
    )
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    def filter_is_favorited(self, queryset, name, value):
        if value and IsAuthenticated:
            return queryset.filter(favorite__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value and IsAuthenticated:
            return queryset.filter(shopping_cart__user=self.request.user)
        return queryset

    class Meta:
        model = Recipes
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')


class IngredientsFilters(SearchFilter):
    """Поиск игредиентов по наименованию."""
    search_param = 'name'
