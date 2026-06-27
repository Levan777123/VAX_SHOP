from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Order, OrderItem, Product, Review
from .tasks import send_order_confirmation_email


def invalidate_product_cache():
    cache.delete('product_stats')
    try:
        cache.delete_pattern('products_list:*')
    except AttributeError:
        pass


@receiver([post_save, post_delete], sender=Product)
@receiver([post_save, post_delete], sender=OrderItem)
@receiver([post_save, post_delete], sender=Review)
def clear_product_cache(sender, **kwargs):
    invalidate_product_cache()


@receiver(post_save, sender=Order)
def order_created(sender, instance, created, **kwargs):
    if created:
        send_order_confirmation_email.delay(instance.id)
