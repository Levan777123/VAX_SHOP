import pytest


@pytest.mark.django_db
def test_register_valid_user(api_client):
    response = api_client.post('/api/auth/register/', {
        'username': 'newcustomer',
        'email': 'new@test.com',
        'password': 'pass12345',
        'role': 'customer',
    }, format='json')
    assert response.status_code == 201
    assert response.data['username'] == 'newcustomer'


@pytest.mark.django_db
def test_register_invalid_user(api_client):
    response = api_client.post('/api/auth/register/', {
        'username': '',
        'password': '123',
        'role': 'bad-role',
    }, format='json')
    assert response.status_code == 400


@pytest.mark.django_db
def test_login_returns_tokens(api_client, customer):
    response = api_client.post('/api/auth/login/', {
        'username': 'customer1',
        'password': 'pass12345',
    }, format='json')
    assert response.status_code == 200
    assert 'access' in response.data
    assert 'refresh' in response.data
