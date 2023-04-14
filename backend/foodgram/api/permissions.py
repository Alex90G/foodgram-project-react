from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied


class AuthorAdminOrReadOnly(permissions.BasePermission):
    """Класс для определения прав доступа."""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        user = request.user
        if user.is_authenticated and user.is_block:
            raise PermissionDenied('Профиль заблокирован.')
        return user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        user = request.user
        if user.is_authenticated and user.is_block:
            raise PermissionDenied('Профиль заблокирован.')
        return (
            user.is_authenticated and (
                obj.author == user or user.is_staff
            )
        )
