from django.contrib.auth import get_user_model
from django.db.models import F, Sum
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse
from djoser.views import UserViewSet as UserHandleSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from api.filters import IngredientFilter, RecipeFilter
from api.pagination import LimitPageNumberPagination
from api.permissions import IsAdminOrReadOnly, IsOwnerOrReadOnly
from api.serializers import (
    FavoriteOrFollowSerializer, FollowSerializer, IngredientSerializer,
    RecipeSerializer, TagSerializer
)
from foodgram.settings import SHOPPING_LIST_NAME, SHOPPING_LIST_STRING
from recipes.models import (Ingredient, RecipeIngredient, Recipe, Tag,
                            Favorite, ShoppingCart)
from users.models import Follow


User = get_user_model()


class UserViewSet(UserHandleSet):
    """Вьюсет для управления пользователями и подписками."""
    lookup_url_kwarg = 'author_id'

    @action(methods=['POST', 'DELETE'], detail=True,)
    def subscribe(self, request, author_id):
        author = get_object_or_404(User, id=author_id)
        if request.method == 'POST':
            if request.user.id == author.id:
                raise ValueError('Нельзя подписаться на себя самого')
            else:
                serializer = FollowSerializer(
                    Follow.objects.create(user=request.user, author=author),
                    context={'request': request})
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            if Follow.objects.filter(user=request.user,
                                     author=author).exists():
                Follow.objects.filter(user=request.user,
                                      author=author).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        serializer = FollowSerializer(
            self.paginate_queryset(Follow.objects.filter(user=request.user)),
            many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)


class TagsViewSet(ReadOnlyModelViewSet):
    permission_classes = (IsAdminOrReadOnly,)
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientsViewSet(ReadOnlyModelViewSet):
    permission_classes = (IsAdminOrReadOnly,)
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientFilter,)
    search_fields = ('^name',)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = LimitPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filter_class = RecipeFilter
    permission_classes = (IsOwnerOrReadOnly,)

    def new_favorite_or_cart_object(self, model, user, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        model.objects.create(user=user, recipe=recipe)
        serializer = FavoriteOrFollowSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def remove_favorite_or_cart(self, model, user, pk):
        obj = model.objects.filter(user=user, recipe__id=pk)
        if obj.exists():
            obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['POST', 'DELETE'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        """Добавить рецепт в 'избранное' или удалить из него."""
        if request.method == 'POST':
            return self.new_favorite_or_cart_object(Favorite, request.user, pk)
        elif request.method == 'DELETE':
            return self.remove_favorite_or_cart(Favorite, request.user, pk)
        return None

    @action(detail=True, methods=['POST', 'DELETE'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        """Добавить рецепт в список покупок или удалить из него."""
        if request.method == 'POST':
            return self.new_favorite_or_cart_object(ShoppingCart,
                                                    request.user, pk)
        elif request.method == 'DELETE':
            return self.remove_favorite_or_cart(ShoppingCart,
                                                request.user, pk)
        return None

    @action(detail=False, methods=['GET'],
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        """Метод, реализующий скачивание списка покупок в виде файла."""
        shopping_list = RecipeIngredient.objects.filter(
            recipe__shopping_cart__user=request.user).values(
            name=F('ingredient__name'),
            measurement_unit=F('ingredient__measurement_unit')).annotate(
            total_amount=Sum('amount'))

        text = '\n'.join([SHOPPING_LIST_STRING.format(
               item['name'], item['measurement_unit'],
               item['total_amount'])
            for item in shopping_list])
        response = HttpResponse(text, content_type='text/plain')
        response['Content-Disposition'] = (
            f'attachment; 'f'filename={SHOPPING_LIST_NAME}')
        return response
