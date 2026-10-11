from datetime import date, datetime, timezone as dt_timezone
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest
from django.core.exceptions import ValidationError
from promo.models import PromoCode
from products.models import SaleItem
from products.models.validator import UserValidatorMixin

pytestmark = pytest.mark.unit


@pytest.mark.parametrize('quantity,price,discount,valid,expected', [
    (1, '100', 10, True, '90'), (3, '0.99', 100, True, '0'),

])
def test_item_discount_uses_mocked_promo(quantity, price, discount, valid, expected):
    # Arrange: метод модели вызывается без ORM; связанные сущности заменены моками.
    promo = Mock(discount_percent=discount)
    promo.is_valid.return_value = valid
    item = SimpleNamespace(quantity=quantity, unit_price=Decimal(price),
                           sale=SimpleNamespace(promo_code=promo))
    item.total_price = SaleItem.total_price.fget(item)
    # Act
    actual = SaleItem.discounted_total_price.fget(item)
    # Assert
    assert actual == Decimal(expected)
    promo.is_valid.assert_called_once_with()


@pytest.mark.parametrize('birthday,valid', [
    (date(2008, 10, 11), True), (date(2008, 10, 12), False),

    (date(2004, 2, 29), True),
])
def test_age_validation_at_eighteenth_birthday(birthday, valid):
    # Arrange
    now = datetime(2026, 10, 11, tzinfo=dt_timezone.utc)
    with patch('products.models.validator.timezone.now', return_value=now):
        # Act / Assert
        if valid:
            UserValidatorMixin.validate_birth_date(birthday)
        else:
            with pytest.raises(ValidationError, match='18'):
                UserValidatorMixin.validate_birth_date(birthday)


@pytest.mark.parametrize('active,start,end,expected', [
    (True, 0, 0, True),
    (False, -1, 1, False), (True, -2, -1, False),
])
def test_promo_validity_includes_both_time_boundaries(active, start, end, expected):
    # Arrange
    from datetime import timedelta
    now = datetime(2026, 10, 11, tzinfo=dt_timezone.utc)
    promo = PromoCode(code='BOUNDARY', discount_percent=10, is_active=active,
                      valid_from=now + timedelta(days=start), valid_to=now + timedelta(days=end))
    with patch('promo.models.timezone.now', return_value=now):
        # Act
        actual = promo.is_valid()
    # Assert
    assert actual is expected


@pytest.mark.parametrize('phone,valid', [('+375 (29) 123-45-67', True), ('123', False),])
def test_supplier_phone_validator_rejects_invalid_formats(phone, valid):
    # Arrange
    from products.models.suppliers import validate_phone
    # Act / Assert
    if valid:
        validate_phone(phone)
    else:
        with pytest.raises(ValidationError):
            validate_phone(phone)
