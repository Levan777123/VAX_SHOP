import pytest
from apps.shop.models import Order, Product


@pytest.mark.django_db
def test_customer_can_order_product(api_client, customer, product):
    api_client.force_authenticate(user=customer)
    response = api_client.post('/api/orders/', {
        'shipping_address': 'Tbilisi, Georgia',
        'checkout_password': 'pass12345',
        'items': [{'product_id': product.id, 'quantity': 2}],
    }, format='json')
    assert response.status_code == 201
    assert response.data['total_price'] == '179.98'
    product.refresh_from_db()
    assert product.stock == 8


@pytest.mark.django_db
def test_order_fails_when_stock_is_empty(api_client, customer, product):
    product.stock = 0
    product.status = Product.Status.PUBLISHED
    product.save()
    api_client.force_authenticate(user=customer)
    response = api_client.post('/api/orders/', {
        'shipping_address': 'Tbilisi, Georgia',
        'checkout_password': 'pass12345',
        'items': [{'product_id': product.id, 'quantity': 1}],
    }, format='json')
    assert response.status_code == 400


@pytest.mark.django_db
def test_order_requires_items(api_client, customer):
    api_client.force_authenticate(user=customer)
    response = api_client.post('/api/orders/', {
        'shipping_address': 'Tbilisi, Georgia',
        'checkout_password': 'pass12345',
        'items': [],
    }, format='json')
    assert response.status_code == 400


@pytest.mark.django_db
def test_order_requires_correct_password(api_client, customer, product):
    api_client.force_authenticate(user=customer)
    response = api_client.post('/api/orders/', {
        'shipping_address': 'Tbilisi, Georgia',
        'checkout_password': 'wrong-password',
        'items': [{'product_id': product.id, 'quantity': 1}],
    }, format='json')
    assert response.status_code == 400


@pytest.mark.django_db
def test_customer_sees_only_own_orders(api_client, customer, other_customer):
    Order.objects.create(user=other_customer, shipping_address='Other address', total_price='10.00')
    api_client.force_authenticate(user=customer)
    response = api_client.get('/api/orders/')
    assert response.status_code == 200
    assert response.data['count'] == 0


@pytest.mark.django_db
def test_customer_cannot_update_order_status(api_client, customer, product):
    order = Order.objects.create(user=customer, shipping_address='Tbilisi', total_price='1.00')
    api_client.force_authenticate(user=customer)
    response = api_client.patch(f'/api/orders/{order.id}/', {'status': 'shipped'}, format='json')
    assert response.status_code == 403
