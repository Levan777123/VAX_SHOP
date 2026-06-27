from decimal import Decimal

import pytest
from apps.shop.models import Product


@pytest.mark.django_db
def test_manager_can_create_product(api_client, manager, category, brand):
    api_client.force_authenticate(user=manager)
    response = api_client.post('/api/products/', {
        'title': 'VAX Wheels 54mm',
        'description': 'Fast street wheels.',
        'sku': 'VAX-WHEELS-54',
        'category': category.id,
        'brand': brand.id,
        'status': 'published',
        'price': '34.90',
        'stock': 20,
    }, format='json')
    assert response.status_code == 201
    assert response.data['created_by'] == manager.id


@pytest.mark.django_db
def test_customer_cannot_create_product(api_client, customer, category, brand):
    api_client.force_authenticate(user=customer)
    response = api_client.post('/api/products/', {
        'title': 'Fake Product',
        'description': 'Should not be created.',
        'sku': 'NOPE-1',
        'category': category.id,
        'brand': brand.id,
        'status': 'published',
        'price': '10.00',
        'stock': 1,
    }, format='json')
    assert response.status_code == 403


@pytest.mark.django_db
def test_product_list_is_public(api_client, product):
    response = api_client.get('/api/products/')
    assert response.status_code == 200
    assert response.data['count'] >= 1


@pytest.mark.django_db
def test_filter_products_by_status(api_client, product, manager, category, brand):
    Product.objects.create(
        title='Draft Deck', description='Hidden draft', sku='DRAFT-1', created_by=manager,
        category=category, brand=brand, status=Product.Status.DRAFT, price=Decimal('10.00'), stock=1,
    )
    response = api_client.get('/api/products/?status=published')
    assert response.status_code == 200
    assert all(item['status'] == 'published' for item in response.data['results'])


@pytest.mark.django_db
def test_manager_can_edit_any_product(api_client, other_manager, product):
    api_client.force_authenticate(user=other_manager)
    response = api_client.patch(f'/api/products/{product.id}/', {'price': '1.00'}, format='json')
    assert response.status_code == 200


@pytest.mark.django_db
def test_product_owner_can_delete_product(api_client, manager, product):
    api_client.force_authenticate(user=manager)
    response = api_client.delete(f'/api/products/{product.id}/')
    assert response.status_code == 200
