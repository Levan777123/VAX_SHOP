import django_filters
from .models import Product


class ProductFilter(django_filters.FilterSet):
    price__gte = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    price__lte = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    stock__gte = django_filters.NumberFilter(field_name='stock', lookup_expr='gte')
    stock__lte = django_filters.NumberFilter(field_name='stock', lookup_expr='lte')
    size = django_filters.CharFilter(field_name='size', lookup_expr='iexact')
    size__icontains = django_filters.CharFilter(field_name='size', lookup_expr='icontains')
    category_slug = django_filters.CharFilter(field_name='category__slug', lookup_expr='iexact')
    brand_slug = django_filters.CharFilter(field_name='brand__slug', lookup_expr='iexact')

    class Meta:
        model = Product
        fields = [
            'status', 'department', 'category', 'brand', 'category_slug', 'brand_slug',
            'price__gte', 'price__lte', 'stock__gte', 'stock__lte', 'size', 'size__icontains'
        ]
