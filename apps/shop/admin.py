from django.contrib import admin
from .models import Brand, Category, Order, OrderItem, Product, ProductMedia, Review, Tag


class ProductMediaInline(admin.TabularInline):
    model = ProductMedia
    extra = 1


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('unit_price',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'slug')
    list_filter = ('department',)
    search_fields = ('name', 'slug')


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name', 'slug')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'sku', 'department', 'category', 'brand', 'status', 'price', 'stock', 'size', 'created_by')
    list_filter = ('department', 'status', 'category', 'brand')
    search_fields = ('title', 'description', 'sku', 'size')
    filter_horizontal = ('tags',)
    inlines = [ProductMediaInline]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total_price', 'created_at')
    list_filter = ('status', 'created_at')
    inlines = [OrderItemInline]


admin.site.register(Tag)
admin.site.register(Review)
