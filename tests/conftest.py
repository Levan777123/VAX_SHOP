from decimal import Decimal

import pytest
from celery import current_app
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.shop.models import Brand, Category, Product


@pytest.fixture(autouse=True)
def eager_celery(settings):
    settings.CELERY_TASK_ALWAYS_EAGER = True
    settings.EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
    current_app.conf.task_always_eager = True
    current_app.conf.task_eager_propagates = True


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def manager(db):
    User = get_user_model()
    return User.objects.create_user(username='manager1', email='manager1@test.com', password='pass12345', role='manager')


@pytest.fixture
def other_manager(db):
    User = get_user_model()
    return User.objects.create_user(username='manager2', email='manager2@test.com', password='pass12345', role='manager')


@pytest.fixture
def customer(db):
    User = get_user_model()
    return User.objects.create_user(username='customer1', email='customer1@test.com', password='pass12345', role='customer')


@pytest.fixture
def other_customer(db):
    User = get_user_model()
    return User.objects.create_user(username='customer2', email='customer2@test.com', password='pass12345', role='customer')


@pytest.fixture
def category(db):
    return Category.objects.create(name='Test Decks', slug='test-decks', department='skate')


@pytest.fixture
def brand(db):
    return Brand.objects.create(name='VAX Original', slug='vax-original')


@pytest.fixture
def product(db, manager, category, brand):
    return Product.objects.create(
        title='VAX Street Deck',
        description='A strong 8.25 inch skateboard deck for street skating.',
        sku='VAX-DECK-825',
        created_by=manager,
        category=category,
        brand=brand,
        status=Product.Status.PUBLISHED,
        price=Decimal('89.99'),
        stock=10,
    )
