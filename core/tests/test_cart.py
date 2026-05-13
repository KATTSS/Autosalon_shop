from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from products.models import Product, Supplier, Supply


class CartViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.product = Product.objects.create(article='C001', name='Cart Product', price=100.00, stock=10)
        supplier = Supplier.objects.create(name='Supp', address='Addr', phone='+375 (29) 123-45-67')
        Supply.objects.create(product=self.product, supplier=supplier, quantity=10, purchase_date='2024-01-01')
    
    def test_empty_cart(self):
        response = self.client.get(reverse('core:cart'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['cart_items']), 0)
    
    def test_cart_with_items(self):
        session = self.client.session
        session['cart'] = {str(self.product.id): {'quantity': 2}}
        session.save()
        response = self.client.get(reverse('core:cart'))
        self.assertEqual(len(response.context['cart_items']), 1)
        self.assertEqual(response.context['total'], 200.00)
    
    def test_add_to_cart_get_redirects(self):
        response = self.client.get(reverse('core:add_to_cart', kwargs={'product_id': self.product.id}))
        self.assertEqual(response.status_code, 302)


class AddToCartTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.product = Product.objects.create(article='C002', name='Test Product', price=50.00, stock=10)
        supplier = Supplier.objects.create(name='Supp2', address='Addr', phone='+375 (29) 123-45-67')
        Supply.objects.create(product=self.product, supplier=supplier, quantity=10, purchase_date='2024-01-01')
    
    def test_add_to_cart_post(self):
        response = self.client.post(
            reverse('core:add_to_cart', kwargs={'product_id': self.product.id}),
            {'quantity': 2}
        )
        self.assertEqual(response.status_code, 302)
        cart = self.client.session.get('cart', {})
        self.assertIn(str(self.product.id), cart)
        self.assertEqual(cart[str(self.product.id)]['quantity'], 2)
    
    def test_add_too_many(self):
        response = self.client.post(
            reverse('core:add_to_cart', kwargs={'product_id': self.product.id}),
            {'quantity': 100}
        )
        self.assertEqual(response.status_code, 302)
        cart = self.client.session.get('cart', {})
        self.assertNotIn(str(self.product.id), cart)

class UpdateCartTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.product = Product.objects.create(article='C004', name='Update Product', price=50.00, stock=10)
        supplier = Supplier.objects.create(name='Supp3', address='Addr', phone='+375 (29) 123-45-67')
        Supply.objects.create(product=self.product, supplier=supplier, quantity=10, purchase_date='2024-01-01')
        session = self.client.session
        session['cart'] = {str(self.product.id): {'quantity': 2}}
        session.save()
    
    def test_update_quantity(self):
        response = self.client.post(
            reverse('core:update_cart', kwargs={'product_id': self.product.id}),
            {'quantity': 5}
        )
        self.assertEqual(response.status_code, 302)
        cart = self.client.session.get('cart', {})
        self.assertEqual(cart[str(self.product.id)]['quantity'], 5)
    
    def test_update_zero_removes(self):
        response = self.client.post(
            reverse('core:update_cart', kwargs={'product_id': self.product.id}),
            {'quantity': 0}
        )
        self.assertEqual(response.status_code, 302)
        cart = self.client.session.get('cart', {})
        self.assertNotIn(str(self.product.id), cart)