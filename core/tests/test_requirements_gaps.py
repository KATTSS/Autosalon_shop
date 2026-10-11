"""Открытые дефекты спецификации. Strict xfail требует снять отметку после исправления."""
from decimal import Decimal

import pytest
from django.urls import reverse
from django.utils import timezone
from products.models import Sale
from promo.models import PromoCode
from .test_order_scenarios import shop, add

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


@pytest.mark.xfail(strict=True, reason='ISSUE-001: checkout accepts missing pickup point')
def test_checkout_requires_pickup_point(client, shop):
    # Arrange
    _, products, _ = shop
    add(client, products[0], 1)
    # Act
    client.post(reverse('core:checkout'), {})
    # Assert: UC-06 требует отклонить оформление без точки самовывоза.
    assert not Sale.objects.exists()


@pytest.mark.xfail(strict=True, reason='ISSUE-002: order history omits discounted total')
def test_order_history_displays_discounted_total(client, shop):
    # Arrange
    _, products, pickup = shop
    promo = PromoCode.objects.create(code='HISTORY', discount_percent=10,
        valid_from=timezone.now() - timezone.timedelta(days=1),
        valid_to=timezone.now() + timezone.timedelta(days=1))
    add(client, products[0], 2)
    client.post(reverse('core:checkout'), {'pickup_point': pickup.pk, 'promo_code': promo.pk})
    assert Sale.objects.get().discounted_total_amount == Decimal('180')
    # Act
    response = client.get(reverse('core:order_history'))
    # Assert: проверяется HTML, а не только существование суммы в БД/context.
    assert '180.00' in response.content.decode()


@pytest.mark.xfail(strict=True, reason='ISSUE-004: media URL is not served with current DEBUG=False')
def test_generated_chart_is_available_via_its_media_url(client, settings):
    # Arrange
    chart = settings.MEDIA_ROOT / 'charts' / 'popularity.png'
    chart.parent.mkdir(parents=True)
    chart.write_bytes(b'chart-placeholder')
    # Act
    response = client.get('/media/charts/popularity.png')
    # Assert: BG-05 требует доступности графика, не только создания файла.
    assert response.status_code == 200
