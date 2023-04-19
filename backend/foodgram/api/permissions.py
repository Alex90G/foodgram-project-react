from rest_framework import permissions


class AuthorAdminOrReadOnly(permissions.BasePermission):
    """Класс для определения прав доступа."""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        user = request.user
        return user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        user = request.user
        return (
            user.is_authenticated and (
                obj.author == user or user.is_admin or user.is_superuser
            )
        )
