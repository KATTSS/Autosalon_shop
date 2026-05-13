from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from products.models import Customer, Sale, SaleItem, Product, Supplier, Supply


class ProfileViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='profile_test', password='pass')
        self.customer = Customer.objects.create(
            user=self.user, phone='+375 (29) 123-45-67', birth_date='1990-01-01'
        )
        self.product = Product.objects.create(article='P001', name='Product', price=100.00, stock=10)
        supplier = Supplier.objects.create(name='Supp', address='Addr', phone='+375 (29) 123-45-67')
        Supply.objects.create(product=self.product, supplier=supplier, quantity=10, purchase_date='2024-01-01')
        self.client.login(username='profile_test', password='pass')
    
    def test_profile_access(self):
        response = self.client.get(reverse('core:profile'))
        self.assertEqual(response.status_code, 200)
    
    def test_profile_anonymous(self):
        self.client.logout()
        response = self.client.get(reverse('core:profile'))
        self.assertEqual(response.status_code, 302)
    
    def test_profile_with_orders(self):
        sale = Sale.objects.create(customer=self.customer)
        SaleItem.objects.create(sale=sale, product=self.product, quantity=1, unit_price=self.product.price)
        response = self.client.get(reverse('core:profile'))
        self.assertEqual(response.context['total_orders'], 1)
        self.assertEqual(len(response.context['last_orders']), 1)
    
    def test_profile_without_customer(self):
        Customer.objects.filter(user=self.user).delete()
        self.client.login(username='profile_test', password='pass')
        response = self.client.get(reverse('core:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context['customer'])


class OrderHistoryViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='history_test', password='pass')
        self.customer = Customer.objects.create(
            user=self.user, phone='+375 (29) 123-45-67', birth_date='1990-01-01'
        )
        self.product = Product.objects.create(article='P002', name='Product2', price=100.00, stock=10)
        supplier = Supplier.objects.create(name='Supp', address='Addr', phone='+375 (29) 123-45-67')
        Supply.objects.create(product=self.product, supplier=supplier, quantity=10, purchase_date='2024-01-01')
        self.client.login(username='history_test', password='pass')
    
    def test_order_history(self):
        sale = Sale.objects.create(customer=self.customer)
        SaleItem.objects.create(sale=sale, product=self.product, quantity=1, unit_price=self.product.price)
        response = self.client.get(reverse('core:order_history'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['orders']), 1)
    
    def test_order_history_empty(self):
        response = self.client.get(reverse('core:order_history'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['orders']), 0)


class ProfileUpdateViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='update_test', password='pass')
        self.customer = Customer.objects.create(
            user=self.user, phone='+375 (29) 123-45-67', birth_date='1990-01-01'
        )
        self.client.login(username='update_test', password='pass')
    
    def test_get_edit_page(self):
        response = self.client.get(reverse('core:profile_edit'))
        self.assertEqual(response.status_code, 200)
    
    def test_post_update(self):
        response = self.client.post(reverse('core:profile_edit'), {
            'phone': '+375 (44) 555-55-55',
            'birth_date': '1995-05-05',
        })
        self.assertEqual(response.status_code, 302)
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.phone, '+375 (44) 555-55-55')