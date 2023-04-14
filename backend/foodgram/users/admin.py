from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


class UsersAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name')
    fieldsets = (("User",
                 {"fields": (
                     'username', 'password', 'email',
                     'first_name', 'last_name',
                     'status', 'last_login', 'date_joined')}),)
    search_fields = ('first_name', 'email',)
    list_filter = ('email', 'first_name',)


admin.site.register(User, UsersAdmin)
