from decimal import Decimal

from django.db import transaction
from django.db.models import Avg
from django.utils import timezone
from rest_framework import serializers

from .models import Brand, Category, Order, OrderItem, Product, ProductMedia, Review, Tag


class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.IntegerField(read_only=True, required=False)

    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'department', 'product_count')
        read_only_fields = ('id', 'slug', 'product_count')


class BrandSerializer(serializers.ModelSerializer):
    product_count = serializers.IntegerField(read_only=True, required=False)

    class Meta:
        model = Brand
        fields = ('id', 'name', 'slug', 'product_count')
        read_only_fields = ('id', 'slug', 'product_count')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name')
        read_only_fields = ('id',)


class ProductMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductMedia
        fields = ('id', 'product', 'file', 'uploaded_at')
        read_only_fields = ('id', 'product', 'uploaded_at')


class ProductSerializer(serializers.ModelSerializer):
    review_count = serializers.SerializerMethodField()
    avg_rating = serializers.SerializerMethodField()
    media = ProductMediaSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True)

    class Meta:
        model = Product
        fields = (
            'id', 'title', 'description', 'sku', 'created_by', 'department', 'category',
            'category_name', 'brand', 'brand_name', 'tags', 'status', 'price', 'stock',
            'size', 'main_image', 'hover_image', 'detail_image_1', 'detail_image_2',
            'review_count', 'avg_rating', 'media', 'created_at', 'updated_at'
        )
        read_only_fields = (
            'id', 'created_by', 'category_name', 'brand_name', 'review_count',
            'avg_rating', 'media', 'created_at', 'updated_at'
        )

    def get_review_count(self, obj):
        return obj.reviews.count()

    def get_avg_rating(self, obj):
        value = obj.reviews.aggregate(avg=Avg('rating'))['avg']
        return round(value, 2) if value is not None else None


class OrderItemInputSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)


class OrderItemSerializer(serializers.ModelSerializer):
    product_title = serializers.CharField(source='product.title', read_only=True)
    product_image = serializers.ImageField(source='product.main_image', read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'product_title', 'product_image', 'quantity', 'unit_price', 'subtotal')
        read_only_fields = ('id', 'unit_price', 'subtotal')


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'user', 'username', 'status', 'shipping_address', 'total_price', 'items', 'created_at', 'paid_at')
        read_only_fields = ('id', 'user', 'username', 'total_price', 'items', 'created_at', 'paid_at')


class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemInputSerializer(many=True, write_only=True)

    class Meta:
        model = Order
        fields = ('id', 'shipping_address', 'items')
        read_only_fields = ('id',)

    def validate_items(self, items):
        if not items:
            raise serializers.ValidationError('Order must contain at least one product.')
        product_ids = [item['product_id'] for item in items]
        if len(product_ids) != len(set(product_ids)):
            raise serializers.ValidationError('Duplicate products are not allowed in one order.')
        return items

    @transaction.atomic
    def create(self, validated_data):
        request = self.context['request']
        items_data = validated_data.pop('items')
        products = {
            product.id: product
            for product in Product.objects.select_for_update().filter(
                id__in=[item['product_id'] for item in items_data],
                status=Product.Status.PUBLISHED,
            )
        }

        total = Decimal('0.00')
        order_items = []
        for item in items_data:
            product = products.get(item['product_id'])
            if not product:
                raise serializers.ValidationError({'items': f"Product {item['product_id']} does not exist or is not published."})
            quantity = item['quantity']
            if product.stock < quantity:
                raise serializers.ValidationError({'items': f'Not enough stock for {product.title}.'})
            product.stock -= quantity
            if product.stock == 0:
                product.status = Product.Status.OUT_OF_STOCK
            product.save(update_fields=['stock', 'status', 'updated_at'])
            total += product.price * quantity
            order_items.append(OrderItem(product=product, quantity=quantity, unit_price=product.price))

        order = Order.objects.create(
            user=request.user,
            shipping_address=validated_data['shipping_address'],
            status=Order.Status.PAID,
            total_price=total,
            paid_at=timezone.now(),
        )
        for order_item in order_items:
            order_item.order = order
        OrderItem.objects.bulk_create(order_items)
        return order

    def to_representation(self, instance):
        return OrderSerializer(instance, context=self.context).data


class ReviewSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Review
        fields = ('id', 'user', 'username', 'product', 'rating', 'comment', 'created_at')
        read_only_fields = ('id', 'user', 'product', 'created_at')
        validators = []

    def validate(self, attrs):
        request = self.context.get('request')
        product_pk = self.context.get('product_pk')
        if self.instance is None and request and product_pk:
            if Review.objects.filter(user=request.user, product_id=product_pk).exists():
                raise serializers.ValidationError('You already reviewed this product.')
        return attrs

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError('Rating must be between 1 and 5.')
        return value
