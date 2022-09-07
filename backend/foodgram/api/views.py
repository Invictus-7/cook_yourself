from django.contrib.auth import get_user_model
from django.db.models import F, Sum
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse
from djoser.views import UserViewSet as UserHandleSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from api.filters import IngredientFilter, RecipeFilter
from api.permissions import IsAdminOrReadOnly, IsOwnerOrReadOnly
from api.serializers import (
    FavoriteOrFollowSerializer, FollowSerializer, IngredientSerializer,
    RecipeSerializer, TagSerializer
)
from foodgram.settings import SHOPPING_LIST_NAME, SHOPPING_LIST_STRING
from recipes.models import (
     Ingredient, RecipeIngredient, Recipe, Tag, Favorite, ShoppingCart
)
from users.models import Follow


User = get_user_model()


class UserViewSet(UserHandleSet):
    """Вьюсет для управления пользователями и подписками."""

    @action(methods=('POST',),
            detail=True,
            permission_classes=(IsAuthenticated,))
    def subscribe(self, request, id=None):
        request.data['user_id'] = request.user.id
        request.data['author_id'] = int(id)
        serializer = FollowSerializer(data=request.data,
                                      context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def unsubscribe(self, request, id=None):
        Follow.objects.filter(user=request.user,
                              author=get_object_or_404(User, id=id)).delete()
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
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filter_class = RecipeFilter
    permission_classes = (IsOwnerOrReadOnly,)

    def new_object(self, model, user, pk):
        """Общий метод для добавления объектов в рамках вьюсета."""
        if model.objects.filter(user=user, recipe__id=pk).exists():
            return Response(
                {'errors': 'Такой рецепт уже есть в списке.'},
                status=status.HTTP_400_BAD_REQUEST)
        if model == Favorite or model == ShoppingCart:
            recipe = get_object_or_404(Recipe, id=pk)
            model.objects.create(user=user, recipe=recipe)
            serializer = FavoriteOrFollowSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({'errors': 'Непредусмотренный тип входящих данных.'},
                        status=status.HTTP_400_BAD_REQUEST)

    def remove_object(self, model, user, pk):
        """Общий метод для удаления объектов в рамках вьюсета."""
        obj = model.objects.filter(user=user, recipe__id=pk)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        if model == Favorite or model == ShoppingCart:
            return Response({'errors': 'Объект не существует или уже удален'},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {'errors': 'Непредусмотренный тип входящих данных.'},
            status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['POST', 'DELETE'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        """Добавить рецепт в 'избранное' или удалить из него."""
        if request.method == 'POST':
            return self.new_object(Favorite, request.user, pk)
        elif request.method == 'DELETE':
            return self.remove_object(Favorite, request.user, pk)
        return None

    @action(detail=True, methods=['POST', 'DELETE'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        """Добавить рецепт в список покупок или удалить из него."""
        if request.method == 'POST':
            return self.new_object(ShoppingCart, request.user, pk)
        elif request.method == 'DELETE':
            return self.remove_object(ShoppingCart, request.user, pk)
        return None

    @action(detail=False, methods=['GET'],
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        """Метод, реализующий скачивание списка покупок в виде файла."""
        shopping_list = RecipeIngredient.objects.filter(
            recipe__shopping_cart__user=request.user).values(
            name=F('ingredient__name'),
            measurement_unit=F(
             'ingredient__measurement_unit')).annotate(
             total_amount=Sum('amount'))

        text = '\n'.join([SHOPPING_LIST_STRING.format(
                item['name'], item['measurement_unit'],
                item['total_amount'])
                for item in shopping_list])
        response = HttpResponse(text, content_type='text/plain')
        response['Content-Disposition'] = (
            f'attachment; 'f'filename={SHOPPING_LIST_NAME}')
        return response
