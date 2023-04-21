from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Кастомная модель пользователя."""
    USER = 'user'
    SUPERUSER = 'superuser'
    ADMIN = 'admin'
    ENABLE = 'enable'
    BLOCK = 'block'
    STATUSES = [
        ('enable', ENABLE),
        ('block', BLOCK),
    ]
    ROLES = [
        ('user', USER),
        ('superuser', SUPERUSER),
        ('admin', ADMIN)
    ]
    email = models.EmailField(
        max_length=254,
        unique=True,
        verbose_name='Почта',
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        verbose_name='Логин',
    )
    first_name = models.CharField(
        max_length=150,
        verbose_name='Имя',
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name='Фамилия',
    )
    password = models.CharField(
        max_length=150,
        verbose_name='Пароль',
    )
    status = models.CharField(
        max_length=max(len(status) for _, status in STATUSES),
        choices=STATUSES,
        default=ENABLE,
        verbose_name='Статус',
    )
    role = models.CharField(
        max_length=max(len(role) for _, role in ROLES),
        choices=ROLES,
        default=USER,
        verbose_name='Роль',
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    @property
    def is_admin(self):
        return self.is_staff or self.role == self.ADMIN

    @property
    def is_superuser(self):
        return self.role == self.SUPERUSER

    @property
    def is_user(self):
        return self.role == self.USER

    @property
    def is_block(self):
        return self.status == self.BLOCK

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

    def __str__(self):
        return f'Подписки пользователя {self.user}'
