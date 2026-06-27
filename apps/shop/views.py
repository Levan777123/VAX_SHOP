import hashlib

from django.core.cache import cache
from django.db.models import Avg, Count
from django.db.models.deletion import ProtectedError
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response

from .filters import ProductFilter
from .models import Brand, Category, Order, Product, Review, Tag
from .permissions import (
    HasPurchasedProduct,
    IsManager,
    IsOrderOwnerOrManager,
    IsReviewOwnerOrManager,
)
from .serializers import (
    BrandSerializer,
    CategorySerializer,
    OrderCreateSerializer,
    OrderSerializer,
    ProductMediaSerializer,
    ProductSerializer,
    ReviewSerializer,
    TagSerializer,
)
from .throttles import OrderBurstThrottle


def clear_shop_cache():
    cache.delete('product_stats')
    try:
        cache.delete_pattern('products_list:*')
    except AttributeError:
        cache.clear()


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filterset_class = ProductFilter
    search_fields = ['title', 'description', 'sku', 'size', 'category__name', 'brand__name']
    ordering_fields = ['price', 'created_at', 'updated_at', 'stock', 'title']
    ordering = ['-created_at']

    def get_queryset(self):
        return Product.objects.select_related('created_by', 'category', 'brand').prefetch_related('tags', 'media', 'reviews')

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'media']:
            return [permissions.IsAuthenticated(), IsManager()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
        clear_shop_cache()

    def perform_update(self, serializer):
        serializer.save()
        clear_shop_cache()

    def list(self, request, *args, **kwargs):
        query_hash = hashlib.md5(request.get_full_path().encode()).hexdigest()
        cache_key = f'products_list:{query_hash}'
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return Response(cached_data)
        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=300)
        return response

    def destroy(self, request, *args, **kwargs):
        product = self.get_object()
        try:
            for field_name in ['main_image', 'hover_image', 'detail_image_1', 'detail_image_2']:
                image = getattr(product, field_name, None)
                if image:
                    image.delete(save=False)
            product.delete()
            clear_shop_cache()
            return Response({'detail': 'Product deleted successfully.'}, status=status.HTTP_200_OK)
        except ProtectedError:
            return Response(
                {'detail': 'This product has orders, so it cannot be deleted. Set it to draft or out of stock instead.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        cache_key = 'product_stats'
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return Response(cached_data)

        status_counts = Product.objects.values('status').annotate(count=Count('id'))
        department_counts = Product.objects.values('department').annotate(count=Count('id'))
        data = {
            'shop_name': 'VAX shop',
            'total_products': Product.objects.count(),
            'published_products': Product.objects.filter(status=Product.Status.PUBLISHED).count(),
            'total_orders': Order.objects.count(),
            'total_sold_items': Product.objects.aggregate(total=Count('order_items'))['total'],
            'products_by_status': {item['status']: item['count'] for item in status_counts},
            'products_by_department': {item['department']: item['count'] for item in department_counts},
            'top_products': list(
                Product.objects.annotate(
                    sold_count=Count('order_items'),
                    avg_rating=Avg('reviews__rating'),
                ).order_by('-sold_count', '-avg_rating').values(
                    'id', 'title', 'sold_count', 'avg_rating'
                )[:5]
            ),
        }
        cache.set(cache_key, data, timeout=300)
        return Response(data)

    @action(detail=True, methods=['post'], url_path='media')
    def media(self, request, pk=None):
        product = self.get_object()
        serializer = ProductMediaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(product=product)
        clear_shop_cache()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer

    def get_queryset(self):
        return Category.objects.annotate(product_count=Count('products'))

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsManager()]

    def perform_create(self, serializer):
        serializer.save()
        clear_shop_cache()

    def perform_update(self, serializer):
        serializer.save()
        clear_shop_cache()

    def perform_destroy(self, instance):
        instance.delete()
        clear_shop_cache()


class BrandViewSet(viewsets.ModelViewSet):
    serializer_class = BrandSerializer

    def get_queryset(self):
        return Brand.objects.annotate(product_count=Count('products'))

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsManager()]

    def perform_create(self, serializer):
        serializer.save()
        clear_shop_cache()

    def perform_update(self, serializer):
        serializer.save()
        clear_shop_cache()

    def perform_destroy(self, instance):
        instance.delete()
        clear_shop_cache()


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsManager()]


class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsOrderOwnerOrManager]
    throttle_classes = [OrderBurstThrottle]
    ordering = ['-created_at']

    def get_queryset(self):
        qs = Order.objects.select_related('user').prefetch_related('items__product')
        if self.request.user.role == 'manager':
            return qs
        return qs.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer

    def partial_update(self, request, *args, **kwargs):
        if request.user.role != 'manager':
            return Response({'detail': 'Only managers can update order status.'}, status=status.HTTP_403_FORBIDDEN)
        return super().partial_update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        if request.user.role != 'manager':
            return Response({'detail': 'Only managers can update order status.'}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs['product_pk']).select_related('user', 'product')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['product_pk'] = self.kwargs.get('product_pk')
        return context

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        if self.action == 'create':
            return [permissions.IsAuthenticated(), HasPurchasedProduct()]
        return [permissions.IsAuthenticated(), IsReviewOwnerOrManager()]

    def perform_create(self, serializer):
        product = Product.objects.get(pk=self.kwargs['product_pk'])
        serializer.save(user=self.request.user, product=product)
