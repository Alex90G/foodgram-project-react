import base64

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers

from recipes.models import (FavoriteRecipes, Ingredients,
                            IngredientsForRecipes, Recipes, ShoppingCart, Tags)
from users.models import Follow, User


class Base64ImageField(serializers.ImageField):
    """Сериализатор изображений."""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class CustomCreateUserSerializer(UserCreateSerializer):
    """Сериализатор создания пользователя."""
    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'password'
        )


class CustomUserSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения пользователя."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, author=obj.id).exists()


class FollowRecipesSerializer(serializers.ModelSerializer):
    """Сериализатор подписок на рецепты."""
    class Meta:
        model = Recipes
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowUsersSerializer(serializers.ModelSerializer):
    """Сериализатор подписок на пользователя."""
    id = serializers.ReadOnlyField(source='author.id')
    email = serializers.ReadOnlyField(source='author.email')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count'
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, author=obj.author).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.GET.get('recipes_limit')
        queryset = Recipes.objects.filter(author=obj.author)
        if recipes_limit:
            queryset = queryset[:int(recipes_limit)]
        return FollowRecipesSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return Recipes.objects.filter(author=obj.author).count()


class TagsSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения тегов."""
    class Meta:
        model = Tags
        fields = '__all__'


class IngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения ингредиентов."""
    class Meta:
        model = Ingredients
        fields = '__all__'


class IngredientsForRecipesSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения ингредиентов в рецептах."""
    id = serializers.ReadOnlyField(source='ingredients.id')
    name = serializers.ReadOnlyField(source='ingredients.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredients.measurement_unit'
    )
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientsForRecipes
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipesSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения рецептов."""
    tags = TagsSerializer(read_only=True, many=True)
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()
    ingredients = IngredientsForRecipesSerializer(read_only=True, many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipes
        exclude = ('pub_date', )

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return FavoriteRecipes.objects.filter(
            user=user, recipes=obj.id
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(user=user, recipes=obj.id).exists()

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        ingredients_list = {}
        if ingredients:
            for ingredient in ingredients:
                if ingredient.get('id') in ingredients_list:
                    raise ValidationError(
                        'Ингредиент можно добавить только один раз'
                    )
                if int(ingredient.get('amount')) <= 0:
                    raise ValidationError(
                        'Необходимо добавить количество ингредиента больше 0'
                    )
                ingredients_list[ingredient.get('id')] = (
                    ingredients_list.get('amount')
                )
            return data
        else:
            raise ValidationError('Необходимо добавить ингредиент в рецепт')

    def create(self, validated_data):
        ingredients_list = self.initial_data.get('ingredients')
        image = validated_data.pop('image')
        recipes = Recipes.objects.create(image=image,
                                         author=self.context['request'].user,
                                         **validated_data)
        tags = self.initial_data.get('tags')
        recipes.tags.set(tags)
        for ingredient in ingredients_list:
            current_ingredient = Ingredients.objects.get(
                id=ingredient.get('id')
            )
            IngredientsForRecipes.objects.create(
                ingredients=current_ingredient, recipes=recipes,
                amount=ingredient.get('amount')
            )
        return recipes

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time',
                                                   instance.cooking_time)
        instance.tags.clear()
        tags = self.initial_data.get('tags')
        instance.tags.set(tags)
        instance.save()
        IngredientsForRecipes.objects.filter(recipes=instance).delete()
        ingredients_list = self.initial_data.get('ingredients')
        for ingredient in ingredients_list:
            current_ingredient = Ingredients.objects.get(
                id=ingredient.get('id')
            )
            IngredientsForRecipes.objects.create(
                ingredients=current_ingredient,
                recipes=instance, amount=ingredient.get('amount')
            )
        return instance


class FavoriteRecipesSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения избранных рецептов."""
    id = serializers.ReadOnlyField(source='recipes.id')
    name = serializers.ReadOnlyField(source='recipes.name')
    image = serializers.ImageField(source='recipes.image')
    cooking_time = serializers.ReadOnlyField(source='recipes.cooking_time')

    class Meta:
        model = FavoriteRecipes
        fields = ('id', 'name', 'image', 'cooking_time')


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения списка покупок."""
    id = serializers.ReadOnlyField(source='recipes.id')
    name = serializers.ReadOnlyField(source='recipes.name')
    image = serializers.ImageField(source='recipes.image')
    cooking_time = serializers.ReadOnlyField(source='recipes.cooking_time')

    class Meta:
        model = ShoppingCart
        fields = '__all__'
