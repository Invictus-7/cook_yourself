from django.contrib.auth import get_user_model
from django.db import models

from recipes.validators import color_validator, slug_validator

User = get_user_model()


class Recipe(models.Model):

    name = models.CharField(verbose_name='Название', max_length=100)
    text = models.TextField(verbose_name='Описание')
    cooking_time = models.PositiveIntegerField(
                                    verbose_name='Время приготовления')
    tags = models.ManyToManyField('Tag', verbose_name='Ярлык')
    ingredients = models.ManyToManyField(
        'Ingredient', through='RecipeIngredient', related_name='recipe')
    author = models.ForeignKey(
        User, related_name='recipes', on_delete=models.CASCADE)
    image = models.ImageField(
        verbose_name='Изображение', upload_to='recipe/')
    pub_date = models.DateTimeField(auto_now_add=True,
                                    verbose_name='Дата публикации')

    class Meta:
        ordering = ('-pub_date', 'author', 'name')
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')
    measurement_unit = models.CharField(
                        verbose_name='Единицы измерения', max_length=200)

    class Meta:
        ordering = ('id',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='name_unique_measurement_unit',
            )
        ]

    def __str__(self):
        return f'{self.name[:20]}, {self.measurement_unit}'


class Tag(models.Model):

    name = models.CharField(max_length=200, verbose_name='Название')

    color = models.CharField(verbose_name='Цвет тега', max_length=7,
                             validators=(color_validator,))

    slug = models.SlugField(max_length=200, unique=True, db_index=True,
                            verbose_name='Слаг',
                            validators=(slug_validator,))

    class Meta:
        ordering = ('slug',)
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return f'{self.name[:20]}'


class RecipeIngredient(models.Model):
    """Промежуточная модель рецепт-ингредиент."""
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               verbose_name='Рецепт', related_name='recipe')

    ingredient = models.ForeignKey(Ingredient, null=True,
                                   on_delete=models.CASCADE,
                                   verbose_name='Ингредиент',
                                   related_name='ingredient')
    amount = models.PositiveIntegerField(verbose_name='Количество')

    class Meta:
        ordering = ('id',)
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_and_ingredient',
            )
        ]

    def __str__(self):
        return f'Ингредиент {self.ingredient} нужен для рецепта {self.recipe}'


class RecipeUserList(models.Model):
    """Общий класс-предок для Favorite и Shopping_Cart."""
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               verbose_name='Рецепт')
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             verbose_name='Пользователь')

    class Meta:
        abstract = True
        ordering = ('user', 'recipe')


class Favorite(RecipeUserList):
    class Meta(RecipeUserList.Meta):
        default_related_name = 'favorites'
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_fav_list_user'
            )
        ]

    def __str__(self):
        return (f'@{self.user.username} добавил '
                f'{self.recipe.name[:30]} в избранное.')


class ShoppingCart(RecipeUserList):
    class Meta(RecipeUserList.Meta):
        default_related_name = 'shopping_cart'
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_cart_list_user'
            )
        ]

    def __str__(self):
        return f'Список покупок для {self.recipe.name[:25]}'
