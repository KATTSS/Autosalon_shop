import pytest
from django.test import Client
from django.urls import reverse

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


@pytest.mark.parametrize('route', ['home', 'about', 'contacts', 'privacy', 'login', 'register'])
def test_public_page_is_accessible(client, route):
    # Arrange
    url = reverse(f'core:{route}')
    # Act
    response = client.get(url)
    # Assert
    assert response.status_code == 200


def test_invalid_login_does_not_authenticate(client):
    # Arrange
    data = {'username': 'missing', 'password': 'incorrect'}
    # Act
    response = client.post(reverse('core:login'), data)
    # Assert
    assert response.status_code == 302
    assert '_auth_user_id' not in client.session


def test_csrf_rejects_post_without_token():
    # Arrange
    client = Client(enforce_csrf_checks=True)
    # Act
    response = client.post(reverse('core:login'), {'username': 'missing', 'password': 'incorrect'})
    # Assert
    assert response.status_code == 403


@pytest.mark.parametrize('route', ['checkout', 'statistics'])
def test_anonymous_cannot_access_protected_page(client, route):
    # Arrange
    url = reverse(f'core:{route}')
    # Act
    response = client.get(url)
    # Assert
    assert response.status_code == 302


def test_regular_user_cannot_access_statistics(client, django_user_model):
    # Arrange
    client.force_login(django_user_model.objects.create_user(username='regular'))
    # Act
    response = client.get(reverse('core:statistics'))
    # Assert
    assert response.status_code == 403
