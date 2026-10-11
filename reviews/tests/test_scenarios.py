import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from reviews.models import Review

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


@pytest.mark.scenario
def test_review_creation_moderation_edit_and_delete(client):
    # Arrange
    user = User.objects.create_user(username='reviewer')
    client.force_login(user)
    # Act / Assert: создание → модерация → редактирование → удаление.
    response = client.post(reverse('reviews:add'), {'text': 'Good', 'rating': 5})
    assert response.status_code == 302
    review = Review.objects.get()
    assert review.user == user and review.rating == 5 and review.product is None
    assert not list(client.get(reverse('reviews:list')).context['reviews'])
    review.is_moderated = True
    review.save(update_fields=['is_moderated'])
    assert list(client.get(reverse('reviews:list')).context['reviews']) == [review]
    assert client.post(reverse('reviews:edit', kwargs={'pk': review.pk}), {'text': 'Updated', 'rating': 4}).status_code == 302
    review.refresh_from_db()
    assert review.text == 'Updated' and review.rating == 4
    assert client.post(reverse('reviews:delete', kwargs={'pk': review.pk})).status_code == 302
    assert not Review.objects.exists()


@pytest.mark.parametrize('data', [{'text': 'x', 'rating': 6}])

def test_invalid_review_is_rejected_without_database_write(client, data):
    # Arrange
    client.force_login(User.objects.create_user(username='reviewer'))
    # Act
    response = client.post(reverse('reviews:add'), data)
    # Assert
    assert response.status_code == 200
    assert response.context['form'].errors
    assert not Review.objects.exists()


@pytest.mark.parametrize('action', ['edit', 'delete'])
def test_other_user_cannot_edit_or_delete_review(client, action):
    # Arrange
    owner = User.objects.create_user(username='owner')
    review = Review.objects.create(user=owner, text='Original', rating=5)
    client.force_login(User.objects.create_user(username='other'))
    # Act
    response = client.post(reverse(f'reviews:{action}', kwargs={'pk': review.pk}), {'text': 'Changed', 'rating': 1})
    # Assert
    assert response.status_code == 403
    review.refresh_from_db()
    assert review.text == 'Original'
