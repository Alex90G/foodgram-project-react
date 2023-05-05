from django.core.validators import MinValueValidator
from django.db import models
from users.models import User


class Ingredients(models.Model):
    """Модель хранения ингредиентов."""
    name = models.CharField(
        verbose_name='Название',
        max_length=200,
        unique=True
    )
    measurement_unit = models.CharField(
        verbose_name='Единицы измерения',
        max_length=100
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Tags(models.Model):
    """Модель для описания тегов."""
    name = models.CharField(
        verbose_name='Название',
        max_length=100,
        unique=True
    )
    color = models.CharField(
        max_length=32,
        verbose_name='Цвет',
        default='#E26C2D',
        unique=True
    )
    slug = models.SlugField(
        verbose_name='Слаг',
        unique=True
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipes(models.Model):
    """Модель хранения рецептов."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipies',
        verbose_name='Автор'
    )
    name = models.CharField(
        verbose_name='Название',
        max_length=200
    )
    image = models.ImageField(
        'Картинка',
        upload_to='recipes/'
    )
    text = models.TextField(
        verbose_name='Описание',
        help_text='Текст рецепта'
    )
    tags = models.ManyToManyField(
        Tags,
        related_name='tags',
        verbose_name='Теги',
        help_text='Выберите тег'
    )
    cooking_time = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1)
        ],
        verbose_name='Время приготовляния',
        help_text='Укажите время приготовления рецепта'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientsForRecipes(models.Model):
    """Модель для хранения количества ингредиентов для рецептов."""
    ingredients = models.ForeignKey(
        Ingredients,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Ингредиенты'
    )
    recipes = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='ingredients',
        verbose_name='Рецепты'
    )
    amount = models.PositiveIntegerField(
        'Количество'
    )

    class Meta():
        verbose_name = 'Ингредиент для рецепта'
        verbose_name_plural = 'Ингредиенты для рецептов'

    def __str__(self):
        return f'Рецепт: {self.recipes}, Ингредиенты: {self.ingredients} '


class FavoriteRecipes(models.Model):
    """Модель для хранения избранных рецептов."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_recipes',
        verbose_name='Пользователь'
    )
    recipes = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='Рецепты'
    )

    class Meta():
        ordering = ('-id',)
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'

    def __str__(self):
        return 'Избранные рецепты'


class ShoppingCart(models.Model):
    """Список покупок"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Пользователь'
    )
    recipes = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Рецепт'
    )

    class Meta():
        ordering = ('-id',)
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        models.UniqueConstraint(
            fields=['user', 'recipes'],
            name='unique_together'
        )

    def __str__(self):
        return f'Cписок покупок {self.user}'
