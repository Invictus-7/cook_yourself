from django.contrib.auth.models import AbstractUser
from django.db import models

from foodgram.settings import (MAX_LEN_EMAIL, MAX_LEN_USERNAME,
                               MAX_LEN_PASSWORD)

from users.validators import validate_username

USER = 'user'
ADMIN = 'admin'


class User(AbstractUser):

    ROLES = ((USER, USER), (ADMIN, ADMIN))

    username = models.CharField(
        verbose_name='Имя пользователя',
        max_length=MAX_LEN_USERNAME,
        unique=True,
        validators=(validate_username,))

    first_name = models.CharField(verbose_name='Имя', max_length=150)
    last_name = models.CharField(verbose_name='Фамилия', max_length=150)
    email = models.EmailField(verbose_name='E-mail',
                              max_length=MAX_LEN_EMAIL,
                              unique=True)
    password = models.CharField(verbose_name='Пароль',
                                max_length=MAX_LEN_PASSWORD)
    role = models.CharField(max_length=max(len(role)
                            for role, _ in ROLES), choices=ROLES,
                            default=USER)

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        constraints = [
            models.UniqueConstraint(
                fields=['username', 'email'],
                name='уникальные пользователи'
            )
        ]

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    @property
    def is_admin(self):
        return self.is_staff or self.is_superuser

    @property
    def is_user(self):
        return self.is_user

    def __str__(self):
        return f'@{self.username}: {self.email}.'


class Follow(models.Model):
    user = models.ForeignKey(User, verbose_name='Подписчик',
                             on_delete=models.CASCADE,
                             related_name='follower')
    author = models.ForeignKey(User, verbose_name='Автор',
                               on_delete=models.CASCADE,
                               related_name='following')

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                name="follow_unique_relationships",
                fields=["user", "author"],
            ),
            models.CheckConstraint(
                name="follow_prevent_self_follow",
                check=~models.Q(user=models.F("author")),
            ),
        ]

    def __str__(self):
        return f'@{self.user.username} подписан на @{self.author.username}'

    def get_email_field_name(self):
        return self.author.email
