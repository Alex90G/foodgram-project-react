import base64

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from recipes.models import (FavoriteRecipes, Ingredients,
                            IngredientsForRecipes, Recipes, ShoppingCart, Tags)
from rest_framework import serializers
from users.serializers import CustomUserSerializer


class Base64ImageField(serializers.ImageField):
    """Сериализатор изображений."""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


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
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )


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
        user = self.context.get('request').user
        recipes_id = self.initial_data.get('id')
        if self.context['request'].method == 'DELETE':
            if not Recipes.objects.filter(
                author_id=user.id, id=recipes_id
            ).exists():
                raise serializers.ValidationError(
                    'Рецепт отсутствует в Ваших рецептах.'
                )
        if Recipes.objects.filter(
            author_id=user.id, id=recipes_id
        ).exists() and self.context['request'].method != 'PATCH':
            raise serializers.ValidationError(
                'Данный рецепт уже есть в Ваших рецептах.'
            )
        ingredients = self.initial_data.get('ingredients')
        ingredients_list = {}
        if not ingredients:
            raise ValidationError('Необходимо добавить ингредиент в рецепт')
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

    def adding_ingredients(self, recipes, ingredients):
        ingredients_list = []
        for ingredient in ingredients:
            current_ingredient = Ingredients.objects.get(
                id=ingredient.get('id')
            )
            current_amount = ingredient.get('amount')
            ingredients_list.append(
                IngredientsForRecipes(
                    recipes=recipes,
                    ingredients=current_ingredient,
                    amount=current_amount
                )
            )
        IngredientsForRecipes.objects.bulk_create(ingredients_list)

    def create(self, validated_data):
        ingredients_list = self.initial_data.get('ingredients')
        image = validated_data.pop('image')
        recipes = Recipes.objects.create(image=image,
                                         author=self.context['request'].user,
                                         **validated_data)
        tags = self.initial_data.get('tags')
        recipes.tags.set(tags)
        self.adding_ingredients(recipes, ingredients_list)
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
        self.adding_ingredients(instance, ingredients_list)
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
