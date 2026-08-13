# from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Avg
from .models import Category, Review, Product
from .permissions import IsModerator, IsOwner
from .serializers import (
    CategorySerializer, CategoryListSerializer,
    ReviewSerializer, ReviewListSerializer,
    ProductSerializer, ProductListSerializer,
    ProductReviewsSerializer,
)
from common.validators import validate_age_from_token

@api_view(['GET', 'POST'])
def category_list_api_view(request):
    if request.method == 'GET':
        categories = Category.objects.annotate(products_count=Count('products'))
        serializer = CategoryListSerializer(categories, many=True)
        return Response(data=serializer.data)

    serializer = CategorySerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    category = serializer.save()
    return Response(data=CategorySerializer(category).data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'DELETE'])
def category_detail_api_view(request, id):
    try:
        category = Category.objects.get(id=id)
    except Category.DoesNotExist:
        return Response(
            data={'error': 'Category not found!'},
            status=status.HTTP_404_NOT_FOUND
        )

    if request.method == 'GET':
        data = CategorySerializer(category, many=False).data
        return Response(data=data)

    if request.method == 'PUT':
        serializer = CategorySerializer(category, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        category = serializer.save()
        return Response(data=CategorySerializer(category).data)

    category.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
def review_list_api_view(request):
    if request.method == 'GET':
        reviews = Review.objects.all()
        serializer = ReviewListSerializer(reviews, many=True)
        return Response(data=serializer.data)

    serializer = ReviewSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    review = serializer.save()

    # Пример задачи Celery, запущенной через .delay(): если оставили низкую
    # оценку, асинхронно уведомляем модераторов по почте (SMTP).
    if review.stars <= 2:
        from product.tasks import send_low_rating_alert
        send_low_rating_alert.delay(review.id)

    return Response(data=ReviewSerializer(review).data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'DELETE'])
def review_detail_api_view(request, id):
    try:
        review = Review.objects.get(id=id)
    except Review.DoesNotExist:
        return Response(data={'error': 'review not found'},
                        status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        data = ReviewSerializer(review, many=False).data
        return Response(data=data)

    if request.method == 'PUT':
        serializer = ReviewSerializer(review, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        review = serializer.save()
        return Response(data=ReviewSerializer(review).data)

    review.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def product_list_api_view(request):
    # Список продуктов открыт для всех (публичное чтение).
    if request.method == 'GET':
        products = Product.objects.all()
        serializer = ProductListSerializer(products, many=True)
        return Response(data=serializer.data)

    # Создание продукта (POST) — модераторам запрещено.
    if request.user.is_staff:
        return Response(
            data={'error': 'Модераторам запрещено создавать продукты.'},
            status=status.HTTP_403_FORBIDDEN,
        )

    # Проверка возраста пользователя по дате рождения из JWT токена.
    validate_age_from_token(request)

    serializer = ProductSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    product = serializer.save(owner=request.user)
    return Response(data=ProductSerializer(product).data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticatedOrReadOnly])
def product_detail_api_view(request, id):
    try:
        product = Product.objects.get(id=id)
    except Product.DoesNotExist:
        return Response(data={'error': 'product not found'},
                                status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        data = ProductSerializer(product, many=False).data
        return Response(data=data)

    # PUT/DELETE разрешены владельцу продукта либо модератору (is_staff=True).
    # has_object_permission() не вызывается автоматически во
    # function-based views, поэтому проверяем права вручную.
    is_owner = IsOwner().has_object_permission(request, None, product)
    is_moderator = IsModerator().has_object_permission(request, None, product)

    if not (is_owner or is_moderator):
        return Response(
            data={'error': 'У вас нет прав на изменение или удаление этого продукта.'},
            status=status.HTTP_403_FORBIDDEN,
        )

    if request.method == 'PUT':
        serializer = ProductSerializer(product, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        product = serializer.save()
        return Response(data=ProductSerializer(product).data)

    product.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def product_reviews_api_view(request):
    products = (
        Product.objects
        .prefetch_related('reviews')
        .annotate(rating=Avg('reviews__stars'))
    )
    serializer = ProductReviewsSerializer(products, many=True)
    return Response(data=serializer.data)