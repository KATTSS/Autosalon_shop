from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from products.models import Product, ProductType, Customer, Sale, SaleItem, Supplier, Supply
from django.utils import timezone
from dateutil.relativedelta import relativedelta


class StatisticsViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_superuser(username='admin', password='pass', email='a@a.com')
        self.user = User.objects.create_user(username='user', password='pass')
        
        self.pt = ProductType.objects.create(name='Test Type')
        self.product = Product.objects.create(article='S001', name='Stat Product', price=100.00, stock=10, product_type=self.pt)
        supplier = Supplier.objects.create(name='Supp', address='Addr', phone='+375 (29) 123-45-67')
        Supply.objects.create(product=self.product, supplier=supplier, quantity=10, purchase_date='2024-01-01')
        
        customer = Customer.objects.create(user=self.user, phone='+375 (29) 123-45-67', birth_date='1990-01-01')
        sale = Sale.objects.create(customer=customer)
        SaleItem.objects.create(sale=sale, product=self.product, quantity=2, unit_price=self.product.price)
        sale.calculate_total()
    
    def test_admin_access(self):
        self.client.login(username='admin', password='pass')
        response = self.client.get(reverse('core:statistics'))
        self.assertEqual(response.status_code, 200)
    
    def test_user_denied(self):
        self.client.login(username='user', password='pass')
        response = self.client.get(reverse('core:statistics'))
        self.assertNotEqual(response.status_code, 200)
    
    def test_anonymous_denied(self):
        response = self.client.get(reverse('core:statistics'))
        self.assertNotEqual(response.status_code, 200)
    
    def test_context_data(self):
        self.client.login(username='admin', password='pass')
        response = self.client.get(reverse('core:statistics'))
        self.assertEqual(response.context['total_sales_count'], 1)
        self.assertEqual(response.context['total_products'], 1)
        self.assertEqual(response.context['total_customers'], 1)
        self.assertIn('avg_sale', response.context)
        self.assertIn('popular_types', response.context)