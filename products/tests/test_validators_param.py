import pytest
from django.core.exceptions import ValidationError
from products.models.customers import Customer


valid_phones = [
    '+375 (29) 123-45-67',
    '+375 (44) 555-55-55',
    '+375 (33) 999-99-99',
    '+375 (17) 111-11-11',
]

invalid_phones = [
    '12345',
    '+375 29 1234567',
    'abc',
    '+375 (29) 1234-567',
    '',
    '375 (29) 123-45-67',
    '+375 (29) 1234567',
    '+375(29)1234567',
]


@pytest.mark.parametrize('phone', valid_phones)
def test_phone_valid(phone):
    try:
        Customer.validate_phone(phone)
    except ValidationError:
        pytest.fail(f'Phone {phone} should be valid')


@pytest.mark.parametrize('phone', invalid_phones)
def test_phone_invalid(phone):
    with pytest.raises(ValidationError):
        Customer.validate_phone(phone)