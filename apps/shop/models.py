from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.text import slugify

from .managers import PublishedProductManager


class Category(models.Model):
    class Department(models.TextChoices):
        SKATE = 'skate', 'Skate'
        CLOTHES = 'clothes', 'Clothes'

    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True, blank=True)
    department = models.CharField(max_length=20, choices=Department.choices, default=Department.SKATE)

    class Meta:
        ordering = ['department', 'name']
        verbose_name_plural = 'Categories'
        unique_together = ('name', 'department')

    def __str__(self):
        return f'{self.name} ({self.department})'

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)
            if self.department:
                base = f'{self.department}-{base}'
            self.slug = base
        super().save(*args, **kwargs)


class Brand(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Tag(models.Model):
    name = models.CharField(max_length=80, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        PUBLISHED = 'published', 'Published'
        OUT_OF_STOCK = 'out_of_stock', 'Out of stock'

    class Department(models.TextChoices):
        SKATE = 'skate', 'Skate'
        CLOTHES = 'clothes', 'Clothes'

    title = models.CharField(max_length=180)
    description = models.TextField()
    sku = models.CharField(max_length=60, unique=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='products')
    department = models.CharField(max_length=20, choices=Department.choices, default=Department.SKATE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, related_name='products', null=True, blank=True)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, related_name='products', null=True, blank=True)
    tags = models.ManyToManyField(Tag, related_name='products', blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    size = models.CharField(max_length=60, blank=True)
    main_image = models.ImageField(upload_to='products/main/', null=True, blank=True)
    hover_image = models.ImageField(upload_to='products/hover/', null=True, blank=True)
    detail_image_1 = models.ImageField(upload_to='products/detail/', null=True, blank=True)
    detail_image_2 = models.ImageField(upload_to='products/detail/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()
    published = PublishedProductManager()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class ProductMedia(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='media')
    file = models.ImageField(upload_to='product_media/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PAID = 'paid', 'Paid'
        SHIPPED = 'shipped', 'Shipped'
        CANCELLED = 'cancelled', 'Cancelled'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PAID)
    shipping_address = models.CharField(max_length=255)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Order #{self.id} - {self.user}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='order_items')
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('order', 'product')

    @property
    def subtotal(self):
        return self.quantity * self.unit_price


class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('user', 'product')

    def __str__(self):
        return f'{self.product} - {self.rating}/5'
