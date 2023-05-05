from recipes.models import Recipes
from rest_framework import mixins, status, viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response


class ListRetrieveViewSet(mixins.ListModelMixin,
                          mixins.RetrieveModelMixin,
                          viewsets.GenericViewSet):
    """Обработка запросов по тегам и ингредиентам. """
    pass


class CustomRecipeViewSet(viewsets.ModelViewSet):
    """Класс для обратботки запросов по рецептам."""
    def adding_object(self, serializers, model, user, pk):
        recipes = get_object_or_404(Recipes, id=pk)
        if model.objects.filter(user=user, recipes=recipes).exists():
            return Response(
                f'{recipes} уже есть в {model}',
                status=status.HTTP_400_BAD_REQUEST
            )
        model.objects.create(user=user, recipes=recipes)
        queryset = model.objects.get(user=user, recipes=recipes)
        serializer = serializers(queryset)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def deleting_object(self, model, pk, user):
        recipes = get_object_or_404(Recipes, id=pk)
        if not model.objects.filter(user=user, recipes=recipes).exists():
            return Response(
                f'{recipes} отсутствует в {model}',
                status=status.HTTP_400_BAD_REQUEST
            )
        model.objects.get(user=user, recipes=recipes).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
