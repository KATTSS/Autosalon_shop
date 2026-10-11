from decimal import Decimal
from unittest.mock import patch

import pytest
from django.contrib.auth.models import User
from django.db import DatabaseError
from django.urls import reverse
from django.utils import timezone
from core.models import PickupPoint
from products.models import Customer, Product, Sale, SaleItem, Supplier, Supply
from promo.models import PromoCode

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


@pytest.fixture
def shop(client):
    user = User.objects.create_user(username='buyer')
    customer = Customer.objects.create(user=user, phone='+375 (29) 123-45-67', birth_date='1990-01-01')
    supplier = Supplier.objects.create(name='Supplier', address='Minsk', phone='+375 (29) 123-45-67')
    products = []
    for index in range(2):
        product = Product.objects.create(article=f'SC{index}', name=f'Product {index}', price='100')
        Supply.objects.create(product=product, supplier=supplier, quantity=5, purchase_date='2026-01-01')
        product.refresh_from_db()
        products.append(product)
    pickup = PickupPoint.objects.create(address='Minsk', phone='+375 (29) 123-45-67', working_hours='9-18')
    client.force_login(user)
    return customer, products, pickup


def add(client, product, quantity):
    return client.post(reverse('core:add_to_cart', kwargs={'product_id': product.pk}), {'quantity': quantity})


@pytest.mark.parametrize('discount,terminal', [(None, 'completed'), (10, 'cancelled')])
@pytest.mark.scenario
def test_cart_checkout_pickup_or_cancel_lifecycle(client, shop, discount, terminal):
    # Arrange
    customer, products, pickup = shop
    product = products[0]
    data = {'pickup_point': pickup.pk}
    if discount:
        promo = PromoCode.objects.create(code='SCENARIO', discount_percent=discount,
            valid_from=timezone.now() - timezone.timedelta(days=1),
            valid_to=timezone.now() + timezone.timedelta(days=1))
        data['promo_code'] = promo.pk
    # Act / Assert: Start → Draft; несколько HTTP-запросов с проверкой каждого состояния.
    assert add(client, product, 1).status_code == 302
    assert add(client, product, 1).status_code == 302
    assert client.session['cart'][str(product.pk)]['quantity'] == 2
    assert not Sale.objects.exists()
    update_url = reverse('core:update_cart', kwargs={'product_id': product.pk})
    assert client.post(update_url, {'quantity': 3}).status_code == 302
    assert client.session['cart'][str(product.pk)]['quantity'] == 3
    assert client.post(update_url, {'quantity': 2}).status_code == 302
    cart = client.get(reverse('core:cart'))
    assert cart.context['total'] == Decimal('200')
    # Draft → Pending → Confirmed → [Discounted] → AwaitingPickup
    response = client.post(reverse('core:checkout'), data)
    assert response.status_code == 302
    sale = Sale.objects.get()
    assert sale.customer == customer and sale.pickup_point == pickup
    assert sale.status == Sale.Status.AWAITING_PICKUP
    assert sale.total_amount == Decimal('200')
    assert sale.discounted_total_amount == Decimal('200') * (100 - (discount or 0)) / 100
    assert sale.items.get().quantity == 2
    assert client.session['cart'] == {}
    product.refresh_from_db()
    assert product.stock == product.calculate_stock() == 3
    history = client.get(reverse('core:order_history'))
    assert [order.pk for order in history.context['orders']] == [sale.pk]
    assert history.context['orders'][0].discount == sale.total_amount - sale.discounted_total_amount
    # AwaitingPickup → Completed / Cancelled
    if terminal == 'completed':
        staff = User.objects.create_user(username='staff', is_staff=True)
        client.force_login(staff)
    endpoint = 'core:complete_order' if terminal == 'completed' else 'core:cancel_order'
    response = client.post(reverse(endpoint, kwargs={'pk': sale.pk}))
    assert response.status_code == 302
    sale.refresh_from_db()
    product.refresh_from_db()
    assert sale.status == terminal
    assert product.stock == product.calculate_stock() == (5 if terminal == 'cancelled' else 3)
    # Терминальные состояния: повторный переход запрещён, склад не меняется.
    assert client.post(reverse(endpoint, kwargs={'pk': sale.pk})).status_code == 400
    product.refresh_from_db()
    assert product.stock == (5 if terminal == 'cancelled' else 3)


@pytest.mark.scenario
def test_clear_cart_abandons_draft_without_creating_sale(client, shop):
    # Arrange
    _, products, _ = shop
    product = products[0]
    add(client, product, 1)
    # Act
    response = client.post(reverse('core:remove_from_cart', kwargs={'product_id': product.pk}))
    # Assert
    assert response.status_code == 302
    assert client.session['cart'] == {}
    assert not Sale.objects.exists()
    assert product.calculate_stock() == 5


@pytest.mark.parametrize('failure', ['stock', 'database'])
@pytest.mark.scenario
def test_failed_checkout_rolls_back_previous_items_and_can_be_retried(client, shop, failure):
    # Arrange: первый товар успевает сохраниться до ошибки на втором.
    _, products, pickup = shop
    for product in products:
        add(client, product, 2)
    original = client.session['cart']
    if failure == 'stock':
        session = client.session
        session['cart'][str(products[1].pk)]['quantity'] = 6
        session.save()
        response = client.post(reverse('core:checkout'), {'pickup_point': pickup.pk})
    else:
        create_item = SaleItem.objects.create
        def fail_on_second(**kwargs):
            if kwargs['product'].pk == products[1].pk:
                raise DatabaseError('forced failure')
            return create_item(**kwargs)
        # Act: заменяем только источник отказа БД, первая запись настоящая.
        with patch('core.views.checkout.SaleItem.objects.create', side_effect=fail_on_second):
            response = client.post(reverse('core:checkout'), {'pickup_point': pickup.pk})
    # Assert: Pending → Failed, откат заказа, позиций и складских остатков.
    assert response.status_code == 302
    assert not Sale.objects.exists() and not SaleItem.objects.exists()
    assert client.session['cart']
    for product in products:
        product.refresh_from_db()
        assert product.stock == product.calculate_stock() == 5
    # Act / Assert: повтор после исправления данных создаёт ровно один заказ.
    session = client.session
    session['cart'] = original
    session.save()
    assert client.post(reverse('core:checkout'), {'pickup_point': pickup.pk}).status_code == 302
    assert Sale.objects.count() == 1 and SaleItem.objects.count() == 2


@pytest.mark.parametrize('endpoint', ['core:cancel_order', 'core:complete_order'])
def test_other_customer_cannot_change_order_and_get_cannot_mutate(client, shop, endpoint):
    # Arrange
    _, products, pickup = shop
    add(client, products[0], 1)
    client.post(reverse('core:checkout'), {'pickup_point': pickup.pk})
    sale = Sale.objects.get()
    client.force_login(User.objects.create_user(username='outsider'))
    url = reverse(endpoint, kwargs={'pk': sale.pk})
    # Act
    get_response = client.get(url)
    post_response = client.post(url)
    # Assert
    assert get_response.status_code == 405
    assert post_response.status_code == 403
    sale.refresh_from_db()
    assert sale.status == Sale.Status.AWAITING_PICKUP


@pytest.mark.parametrize('quantity', ['abc', '0', '6'])
def test_invalid_add_quantity_keeps_cart_unchanged(client, shop, quantity):
    # Arrange
    _, products, _ = shop
    # Act
    response = add(client, products[0], quantity)
    # Assert
    assert response.status_code == 302
    assert not client.session.get('cart')


@pytest.mark.parametrize('quantity', ['-1'])
def test_invalid_update_quantity_keeps_existing_quantity(client, shop, quantity):
    # Arrange
    _, products, _ = shop
    product = products[0]
    add(client, product, 2)
    # Act
    response = client.post(reverse('core:update_cart', kwargs={'product_id': product.pk}), {'quantity': quantity})
    # Assert
    assert response.status_code == 302
    assert client.session['cart'][str(product.pk)]['quantity'] == 2


def test_exact_stock_limit_and_missing_cart_item_update(client, shop):
    # Arrange
    _, products, _ = shop
    product = products[0]
    url = reverse('core:update_cart', kwargs={'product_id': product.pk})
    # Act / Assert
    assert client.post(url, {'quantity': 1}).status_code == 302
    assert not client.session.get('cart')
    add(client, product, 5)
    add(client, product, 1)
    assert client.session['cart'][str(product.pk)]['quantity'] == 5
    assert client.post(url, {'quantity': 0}).status_code == 302
    assert client.session['cart'] == {}


def test_deleted_product_does_not_break_checkout_page(client, shop):
    # Arrange
    _, products, _ = shop
    add(client, products[0], 1)
    products[0].delete()
    # Act
    response = client.get(reverse('core:checkout'))
    # Assert
    assert response.status_code == 200
    assert response.context['cart_items'] == []


@pytest.mark.parametrize('quantity', [0])
def test_checkout_rejects_invalid_session_quantity(client, shop, quantity):
    # Arrange
    _, products, pickup = shop
    session = client.session
    session['cart'] = {str(products[0].pk): {'quantity': quantity}}
    session.save()
    # Act
    response = client.post(reverse('core:checkout'), {'pickup_point': pickup.pk})
    # Assert
    assert response.status_code == 302
    assert not Sale.objects.exists()
    assert products[0].calculate_stock() == 5


@pytest.mark.parametrize('source,target', [
    ('confirmed', 'discounted'), ('awaiting_pickup', 'unknown'),
])
def test_invalid_model_transition_preserves_persisted_state(shop, source, target):
    # Arrange
    customer, _, pickup = shop
    sale = Sale.objects.create(customer=customer, pickup_point=pickup, status=source)
    # Act / Assert
    with pytest.raises(ValueError):
        sale.transition_to(target)
    sale.refresh_from_db()
    assert sale.status == source


@pytest.mark.parametrize('discounted', [False, True])
@pytest.mark.scenario
def test_confirmed_to_pickup_model_transitions(shop, discounted):
    # Arrange
    customer, _, pickup = shop
    promo = PromoCode.objects.create(code='TRANSITION', discount_percent=10,
        valid_from=timezone.now() - timezone.timedelta(days=1),
        valid_to=timezone.now() + timezone.timedelta(days=1)) if discounted else None
    sale = Sale.objects.create(customer=customer, pickup_point=pickup,
                               status=Sale.Status.CONFIRMED, promo_code=promo)
    # Act / Assert
    if discounted:
        sale.transition_to(Sale.Status.DISCOUNTED)
        sale.refresh_from_db()
        assert sale.status == Sale.Status.DISCOUNTED
    sale.transition_to(Sale.Status.AWAITING_PICKUP)
    sale.refresh_from_db()
    assert sale.status == Sale.Status.AWAITING_PICKUP


@pytest.mark.parametrize('active', [True])
def test_invalid_or_expired_promo_does_not_discount_order(client, shop, active):
    # Arrange
    _, products, pickup = shop
    now = timezone.now()
    promo = PromoCode.objects.create(code='INVALID', discount_percent=10, is_active=active,
        valid_from=now - timezone.timedelta(days=2), valid_to=now - timezone.timedelta(days=1))
    add(client, products[0], 1)
    # Act
    response = client.post(reverse('core:checkout'), {'pickup_point': pickup.pk, 'promo_code': promo.pk})
    # Assert
    assert response.status_code == 302
    sale = Sale.objects.get()
    assert sale.promo_code is None
    assert sale.total_amount == sale.discounted_total_amount == Decimal('100')
    assert sale.status == Sale.Status.AWAITING_PICKUP


def test_order_history_is_newest_first_and_excludes_other_customers(client, shop):
    # Arrange
    customer, _, pickup = shop
    old = Sale.objects.create(customer=customer, pickup_point=pickup)
    new = Sale.objects.create(customer=customer, pickup_point=pickup)
    Sale.objects.filter(pk=old.pk).update(sale_date=timezone.now() - timezone.timedelta(days=1))
    other = Customer.objects.create(user=User.objects.create_user(username='other'),
                                   phone='+375 (29) 123-45-67', birth_date='1990-01-01')
    Sale.objects.create(customer=other)
    # Act
    response = client.get(reverse('core:order_history'))
    # Assert
    assert [order.pk for order in response.context['orders']] == [new.pk, old.pk]
