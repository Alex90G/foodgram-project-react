from djoser.views import UserViewSet
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from api.pagination import CustomPageNumberPagination
from users.models import Follow, User
from users.serializers import FollowUsersSerializer


class CustomUserViewSet(UserViewSet):
    """
    Обрабатывает запросы к странице пользователя.
    """
    pagination_class = CustomPageNumberPagination

    @action(detail=False, permission_classes=[permissions.IsAuthenticated])
    def subscriptions(self, request):
        queryset = Follow.objects.filter(user=request.user)
        page = self.paginate_queryset(queryset)
        serializer = FollowUsersSerializer(
            page, many=True,
            context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, id=id)
        if request.method == "POST":
            if user == author or Follow.objects.filter(
                user=user, author=author
            ).exists():
                return Response('Ошибка подписки',
                                status=status.HTTP_400_BAD_REQUEST)
            Follow.objects.create(user=user, author=author)
            queryset = Follow.objects.get(user=request.user, author=author)
            serializer = FollowUsersSerializer(
                queryset,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == "DELETE":
            if not Follow.objects.filter(user=user, author=author).exists():
                return Response('Подписка отсутствует.',
                                status=status.HTTP_400_BAD_REQUEST)
            Follow.objects.get(user=user, author=author).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
