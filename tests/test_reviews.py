import pytest
from apps.shop.models import Order, OrderItem, Review


@pytest.fixture
def paid_order(customer, product):
    order = Order.objects.create(user=customer, shipping_address='Tbilisi', total_price=product.price, status=Order.Status.PAID)
    OrderItem.objects.create(order=order, product=product, quantity=1, unit_price=product.price)
    return order


@pytest.mark.django_db
def test_purchased_customer_can_review(api_client, customer, product, paid_order):
    api_client.force_authenticate(user=customer)
    response = api_client.post(f'/api/products/{product.id}/reviews/', {
        'rating': 5,
        'comment': 'Perfect deck for street skating.',
    }, format='json')
    assert response.status_code == 201
    assert response.data['rating'] == 5


@pytest.mark.django_db
def test_unpurchased_customer_cannot_review(api_client, other_customer, product):
    api_client.force_authenticate(user=other_customer)
    response = api_client.post(f'/api/products/{product.id}/reviews/', {
        'rating': 5,
        'comment': 'I did not buy it.',
    }, format='json')
    assert response.status_code == 403


@pytest.mark.django_db
def test_duplicate_review_is_rejected(api_client, customer, product, paid_order):
    Review.objects.create(user=customer, product=product, rating=5, comment='First review')
    api_client.force_authenticate(user=customer)
    response = api_client.post(f'/api/products/{product.id}/reviews/', {
        'rating': 4,
        'comment': 'Second review',
    }, format='json')
    assert response.status_code == 400


@pytest.mark.django_db
def test_other_customer_cannot_edit_review(api_client, customer, other_customer, product):
    review = Review.objects.create(user=customer, product=product, rating=5, comment='Owner review')
    api_client.force_authenticate(user=other_customer)
    response = api_client.patch(f'/api/products/{product.id}/reviews/{review.id}/', {
        'comment': 'Trying to edit',
    }, format='json')
    assert response.status_code == 403
