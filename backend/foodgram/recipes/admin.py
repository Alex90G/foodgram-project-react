from django.contrib import admin

from .models import (FavoriteRecipes, Ingredients, IngredientsForRecipes,
                     Recipes, ShoppingCart, Tags)


class TagsAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
    search_fields = ('name', 'slug',)


class IngredientsAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)


class IngredientsInLine(admin.StackedInline):
    model = IngredientsForRecipes
    extra = 5


class RecipesAdmin(admin.ModelAdmin):
    list_display = ('author', 'name', 'text', 'cooking_time', 'favorite')
    list_filter = ('author', 'name', 'tags')
    inlines = [IngredientsInLine]

    def favorite(self, obj):
        return obj.favorite.count()


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipes')
    search_fields = ('user', 'recipes',)


class FavoriteRecipesAdmin(admin.ModelAdmin):
    list_display = ('recipes', 'user')
    list_filter = ('user',)


admin.site.register(Tags, TagsAdmin)
admin.site.register(Ingredients, IngredientsAdmin)
admin.site.register(Recipes, RecipesAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(FavoriteRecipes, FavoriteRecipesAdmin)
