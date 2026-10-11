"""Проверки бизнес-данных вместо одного лишь HTTP 200 на пустой странице."""
from datetime import datetime, timezone as dt_timezone
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from products.models import Product, ProductType, Manufacturer, Customer, Sale, SaleItem, Supply, Supplier
from news.models import Article
from faq.models import FAQItem
from vacancies.models import Vacancy

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


@pytest.fixture
def catalog():
    category = ProductType.objects.create(name='Tyres')
    brand = Manufacturer.objects.create(name='Brand')
    a = Product.objects.create(article='CAT-A', name='Alpha', price=100, stock=3,
                               product_type=category, manufacturer=brand)
    b = Product.objects.create(article='CAT-B', name='Beta', price=200, stock=2)
    Product.objects.create(article='CAT-Z', name='Invisible', price=50, stock=0)
    return a, b


@pytest.mark.parametrize('query,expected', [
    ({}, ['CAT-A', 'CAT-B']), ({'q': 'alp'}, ['CAT-A']), ({'q': 'CAT-B'}, ['CAT-B']),
    ({'price_min': 200}, ['CAT-B']), ({'price_max': 100}, ['CAT-A']),
    ({'sort': 'price_desc'}, ['CAT-B', 'CAT-A']),
])

def test_catalog_search_price_boundaries_stock_and_sort(client, catalog, query, expected):
    # Arrange: каталог содержит две доступные позиции и одну без остатка.
    # Act
    response = client.get(reverse('core:catalog'), query)
    # Assert
    assert response.status_code == 200
    assert [p.article for p in response.context['products']] == expected


@pytest.mark.parametrize('filter_name,field', [('category', 'product_type_id'), ('manufacturer', 'manufacturer_id')])
def test_catalog_filters_by_related_entity(client, catalog, filter_name, field):
    # Arrange
    selected = getattr(catalog[0], field)
    # Act
    response = client.get(reverse('core:catalog'), {filter_name: selected})
    # Assert
    assert list(response.context['products']) == [catalog[0]]


def test_catalog_pagination_and_related_products(client, catalog):
    # Arrange
    for i in range(11):
        Product.objects.create(article=f'PAGE{i}', name=f'Page {i}', price=10, stock=1,
                               product_type=catalog[0].product_type)
    # Act
    first = client.get(reverse('core:catalog'))
    second = client.get(reverse('core:catalog'), {'page': 2})
    detail = client.get(reverse('core:product_detail', kwargs={'pk': catalog[0].pk}))
    # Assert
    assert len(first.context['products']) == 12
    assert len(second.context['products']) == 1
    related = detail.context['related_products']
    assert len(related) == 4
    assert all(p.product_type == catalog[0].product_type and p.pk != catalog[0].pk for p in related)
    assert client.get(reverse('core:product_detail', kwargs={'pk': 99999})).status_code == 404


@pytest.mark.parametrize('phone,birthday,error_field', [
    ('123', '1990-01-01', 'phone'), ('+375 (29) 123-45-67', '2020-01-01', 'birth_date'),
])
def test_registration_invalid_input_creates_neither_user_nor_customer(client, phone, birthday, error_field):
    # Arrange
    data = dict(username='invalid', email='user@example.com', phone=phone, birth_date=birthday,
                password1='Strong-password-987', password2='Strong-password-987')
    # Act
    response = client.post(reverse('core:register'), data)
    # Assert
    assert response.status_code == 200
    assert error_field in response.context['form'].errors
    assert not User.objects.exists() and not Customer.objects.exists()


def test_register_login_and_logout_persist_linked_profile(client):
    # Arrange
    data = dict(username='registered', email='user@example.com', phone='+375 (29) 123-45-67',
                birth_date='1990-01-01', password1='Strong-password-987', password2='Strong-password-987')
    # Act / Assert
    assert client.post(reverse('core:register'), data).status_code == 302
    user = User.objects.get(username='registered')
    assert Customer.objects.get(user=user).phone == data['phone']
    assert user.check_password(data['password1'])
    assert client.post(reverse('core:login'), {'username': user.username, 'password': data['password1']}).status_code == 302
    assert int(client.session['_auth_user_id']) == user.pk
    assert client.get(reverse('core:logout')).status_code == 302
    assert '_auth_user_id' not in client.session


def test_public_content_filters_publication_and_orders_faq(client):
    # Arrange
    visible = Article.objects.create(title='Visible', slug='visible', short_text='x', full_text='x', image='news/test.png')
    hidden = Article.objects.create(title='Hidden', slug='hidden', short_text='x', full_text='x', is_published=False)
    first = FAQItem.objects.create(question='First', answer='x', order=1)
    second = FAQItem.objects.create(question='Second', answer='x', order=2)
    FAQItem.objects.create(question='Hidden', answer='x', order=0, is_published=False)
    vacancy = Vacancy.objects.create(title='Active', description='x', requirements='x', conditions='x')
    Vacancy.objects.create(title='Inactive', description='x', requirements='x', conditions='x', is_active=False)
    # Act / Assert
    assert list(client.get(reverse('news:list')).context['articles']) == [visible]
    assert client.get(visible.get_absolute_url()).status_code == 200
    assert client.get(hidden.get_absolute_url()).status_code == 404
    assert list(client.get(reverse('faq:list')).context['faq_items']) == [first, second]
    assert list(client.get(reverse('vacancies:list')).context['vacancies']) == [vacancy]


def test_statistics_computes_known_aggregates_and_writes_chart(client, settings):
    # Arrange
    user = User.objects.create_user(username='stats', is_superuser=True)
    client.force_login(user)
    now = datetime(2026, 10, 11, tzinfo=dt_timezone.utc)
    category = ProductType.objects.create(name='Parts')
    product = Product.objects.create(article='STATS', name='Part', price=100, product_type=category)
    supplier = Supplier.objects.create(name='Supplier', address='Minsk', phone='+375 (29) 123-45-67')
    Supply.objects.create(product=product, supplier=supplier, quantity=20, purchase_date='2026-01-01')
    customers = []
    for index, birth in enumerate(['1996-10-11', '1986-10-11']):
        buyer = User.objects.create_user(username=f'buyer{index}')
        customers.append(Customer.objects.create(user=buyer, phone='+375 (29) 123-45-67', birth_date=birth))
    for quantity in [1, 2, 2, 3]:
        sale = Sale.objects.create(customer=customers[0])
        SaleItem.objects.create(sale=sale, product=product, quantity=quantity, unit_price=100)
    # Act
    with patch('core.views.statistics.timezone.now', return_value=now):
        response = client.get(reverse('core:statistics'))
    # Assert
    context = response.context
    assert context['total_sales'] == Decimal('800')
    assert context['avg_sale'] == context['median_sale'] == context['mode_sale'] == Decimal('200')
    assert context['avg_age'] == context['median_age'] == 35
    assert context['min_age'] == 30 and context['max_age'] == 40
    assert context['popular_types'][0].total_sold == 8
    assert (Path(settings.MEDIA_ROOT) / 'charts/popularity.png').read_bytes().startswith(b'\x89PNG')
