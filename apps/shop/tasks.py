from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string


@shared_task
def send_order_confirmation_email(order_id):
    from .models import Order

    order = Order.objects.select_related('user').prefetch_related('items__product').get(id=order_id)
    if not order.user.email:
        return 'User has no email address.'

    html_message = render_to_string('emails/order_confirmation.html', {'order': order, 'shop_name': 'VAX shop'})
    send_mail(
        subject=f'VAX shop order #{order.id} confirmation',
        message=f'Thanks for your order #{order.id} at VAX shop.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[order.user.email],
        html_message=html_message,
        fail_silently=False,
    )
    return f'Order confirmation sent for order {order.id}.'


@shared_task
def send_low_stock_report():
    from django.contrib.auth import get_user_model
    from .models import Product

    User = get_user_model()
    managers = User.objects.filter(role='manager', email__isnull=False).exclude(email='')
    products = Product.objects.filter(stock__lte=5).order_by('stock', 'title')
    if not products.exists():
        return 'No low stock products.'

    lines = ['Low stock products in VAX shop:', '']
    for product in products:
        lines.append(f'- {product.title} ({product.sku}): {product.stock} left')

    recipients = list(managers.values_list('email', flat=True))
    if recipients:
        send_mail(
            subject='VAX shop low stock report',
            message='\n'.join(lines),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipients,
            fail_silently=False,
        )
    return f'Low stock report sent to {len(recipients)} manager(s).'
