from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from products.models import Product, Customer, Sale, Supplier, Supply
from core.models import PickupPoint


class CheckoutViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='checkout_test', password='pass')
        self.customer = Customer.objects.create(
            user=self.user, phone='+375 (29) 123-45-67', birth_date='1990-01-01'
        )
        self.product = Product.objects.create(article='CH001', name='Checkout Product', price=100.00, stock=10)
        supplier = Supplier.objects.create(name='Supp', address='Addr', phone='+375 (29) 123-45-67')
        Supply.objects.create(product=self.product, supplier=supplier, quantity=10, purchase_date='2024-01-01')
        self.pickup = PickupPoint.objects.create(address='Test', phone='+375 (29) 123-45-67', working_hours='9-18')
        self.client.login(username='checkout_test', password='pass')
    
    
    def test_get_with_items(self):
        session = self.client.session
        session['cart'] = {str(self.product.id): {'quantity': 2}}
        session.save()
        response = self.client.get(reverse('core:checkout'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['cart_items']), 1)
    
    def test_post_empty_cart(self):
        response = self.client.post(reverse('core:checkout'))
        self.assertEqual(response.status_code, 302)
    
    
    


class CheckoutNoCustomerTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='no_customer', password='pass')
        self.product = Product.objects.create(article='CH002', name='Product', price=50.00, stock=10)
        supplier = Supplier.objects.create(name='Supp', address='Addr', phone='+375 (29) 123-45-67')
        Supply.objects.create(product=self.product, supplier=supplier, quantity=10, purchase_date='2024-01-01')
        self.pickup = PickupPoint.objects.create(address='Test', phone='+375 (29) 123-45-67', working_hours='9-18')
        self.client.login(username='no_customer', password='pass')
    
    def test_post_no_customer(self):
        session = self.client.session
        session['cart'] = {str(self.product.id): {'quantity': 1}}
        session.save()
        response = self.client.post(reverse('core:checkout'), {
            'pickup_point': self.pickup.id,
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Sale.objects.count(), 0)
