from django.contrib.auth.models import AbstractUser
from django.db import models

ENABLE = 'enable'
BLOCK = 'block'
STATUSES = [
    ('enable', ENABLE),
    ('block', BLOCK),
]


class User(AbstractUser):
    """Кастомная модель пользователя."""
    email = models.EmailField(
        max_length=254,
        unique=True
    )
    username = models.CharField(
        max_length=150,
        unique=True,
    )
    first_name = models.CharField(
        max_length=150,
    )
    last_name = models.CharField(
        max_length=150,
    )
    password = models.CharField(
        max_length=150,
    )
    status = models.CharField(
        max_length=max(len(status) for _, status in STATUSES),
        choices=STATUSES,
        default=ENABLE
    )

    @property
    def is_block(self):
        return self.status == BLOCK

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Follow(models.Model):
    """Модель для создания и хранения подписок."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'], name='unique_together'
            )
        ]
