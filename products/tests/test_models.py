from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from products.models import Product, ProductType, Manufacturer, Customer, Sale, SaleItem, Supplier, Supply
from django.utils import timezone
from decimal import Decimal
from promo.models import PromoCode


class SaleWithPromoTest(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='buyer2', password='pass')
        self.customer = Customer.objects.create(user=user, phone='+375 (29) 123-45-67', birth_date='1990-01-01')
        self.product = Product.objects.create(article='P002', name='Product2', price=100.00, stock=10)
        supplier = Supplier.objects.create(name='Supp', address='Addr', phone='+375 (29) 123-45-67')
        Supply.objects.create(product=self.product, supplier=supplier, quantity=10, purchase_date='2024-01-01')
        self.promo = PromoCode.objects.create(
            code='SALE10',
            discount_percent=Decimal('10'),
            valid_from=timezone.now() - timezone.timedelta(days=1),
            valid_to=timezone.now() + timezone.timedelta(days=1),
            is_active=True
        )
    
    
    def test_sale_item_no_promo(self):
        sale = Sale.objects.create(customer=self.customer)
        item = SaleItem.objects.create(sale=sale, product=self.product, quantity=2, unit_price=self.product.price)
        self.assertEqual(item.discounted_total_price, item.total_price)
        self.assertEqual(item.discount_amount, 0)


class SaleItemSaveTest(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='buyer3', password='pass')
        self.customer = Customer.objects.create(user=user, phone='+375 (29) 123-45-67', birth_date='1990-01-01')
        self.product = Product.objects.create(article='P003', name='Product3', price=100.00, stock=5)
        supplier = Supplier.objects.create(name='Supp2', address='Addr', phone='+375 (29) 123-45-67')
        Supply.objects.create(product=self.product, supplier=supplier, quantity=5, purchase_date='2024-01-01')
    
    def test_not_enough_stock(self):
        sale = Sale.objects.create(customer=self.customer)
        with self.assertRaises(ValueError):
            SaleItem.objects.create(sale=sale, product=self.product, quantity=10, unit_price=self.product.price)
    
    
    def test_unit_price_auto_set(self):
        sale = Sale.objects.create(customer=self.customer)
        item = SaleItem.objects.create(sale=sale, product=self.product, quantity=1)
        self.assertEqual(item.unit_price, self.product.price)


class ProductTest(TestCase):
    def setUp(self):
        self.pt = ProductType.objects.create(name='Test Type')
        self.m = Manufacturer.objects.create(name='Test Brand')
    
    
    
    
    def test_price_negative_validation(self):
        p = Product(article='A004', name='Bad', price=-10.00)
        with self.assertRaises(ValidationError):
            p.full_clean()
