from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from products.models import Product, ProductType, Manufacturer, Customer, Sale, SaleItem, Supplier, Supply
from django.utils import timezone
from decimal import Decimal
from promo.models import PromoCode
from core.models import PickupPoint


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
    
    def test_sale_with_promo(self):
        sale = Sale.objects.create(customer=self.customer, promo_code=self.promo)
        SaleItem.objects.create(sale=sale, product=self.product, quantity=2, unit_price=self.product.price)
        sale.calculate_total()
        self.assertEqual(sale.total_amount, 200.00)
        self.assertAlmostEqual(sale.discounted_total_amount, 180.00)
    
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
    
    def test_stock_decreases_after_sale(self):
        sale = Sale.objects.create(customer=self.customer)
        self.assertEqual(self.product.calculate_stock(), 5)
        SaleItem.objects.create(sale=sale, product=self.product, quantity=3, unit_price=self.product.price)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 2)
    
    def test_unit_price_auto_set(self):
        sale = Sale.objects.create(customer=self.customer)
        item = SaleItem.objects.create(sale=sale, product=self.product, quantity=1)
        self.assertEqual(item.unit_price, self.product.price)


class SaleStrTest(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='buyer4', password='pass')
        self.customer = Customer.objects.create(user=user, phone='+375 (29) 123-45-67', birth_date='1990-01-01')
    
    def test_str(self):
        sale = Sale.objects.create(customer=self.customer)
        self.assertIn(str(sale.id), str(sale))
        self.assertIn(self.customer.user.username, str(sale))


class SaleWithPickupPointTest(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='buyer5', password='pass')
        self.customer = Customer.objects.create(user=user, phone='+375 (29) 123-45-67', birth_date='1990-01-01')
        self.pickup = PickupPoint.objects.create(address='Test address', phone='+375 (29) 123-45-67', working_hours='9-18')
        self.product = Product.objects.create(article='P004', name='Product4', price=100.00, stock=10)
        supplier = Supplier.objects.create(name='Supp3', address='Addr', phone='+375 (29) 123-45-67')
        Supply.objects.create(product=self.product, supplier=supplier, quantity=10, purchase_date='2024-01-01')
    
    def test_sale_with_pickup(self):
        sale = Sale.objects.create(customer=self.customer, pickup_point=self.pickup)
        SaleItem.objects.create(sale=sale, product=self.product, quantity=1, unit_price=self.product.price)
        self.assertEqual(sale.pickup_point.address, 'Test address')

class ProductTypeTest(TestCase):
    def test_create(self):
        pt = ProductType.objects.create(name='Шины')
        self.assertEqual(str(pt), 'Шины')


class ManufacturerTest(TestCase):
    def test_create(self):
        m = Manufacturer.objects.create(name='Michelin', country='Франция')
        self.assertEqual(str(m), 'Michelin')


class ProductTest(TestCase):
    def setUp(self):
        self.pt = ProductType.objects.create(name='Test Type')
        self.m = Manufacturer.objects.create(name='Test Brand')
    
    def test_create(self):
        p = Product.objects.create(article='A001', name='Test', price=100.00, stock=5)
        self.assertEqual(str(p), 'A001 — Test')
    
    def test_stock_default_zero(self):
        p = Product.objects.create(article='A002', name='Test2', price=50.00)
        self.assertEqual(p.stock, 0)
    
    def test_calculate_stock_no_sales(self):
        p = Product.objects.create(article='A003', name='Test3', price=100.00)
        self.assertEqual(p.calculate_stock(), 0)
    
    def test_price_negative_validation(self):
        p = Product(article='A004', name='Bad', price=-10.00)
        with self.assertRaises(ValidationError):
            p.full_clean()


class CustomerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test', password='pass')
    
    def test_create(self):
        c = Customer.objects.create(user=self.user, phone='+375 (29) 123-45-67', birth_date='1990-01-01')
        self.assertEqual(c.user.username, 'test')
    
    def test_phone_validation(self):
        Customer.validate_phone('+375 (29) 123-45-67')
        with self.assertRaises(ValidationError):
            Customer.validate_phone('12345')
    
    def test_age_property(self):
        c = Customer.objects.create(user=self.user, phone='+375 (29) 123-45-67', birth_date='1990-01-01')
        self.assertIsNotNone(c.age)
    
    def test_under_18_validation(self):
        c = Customer(user=self.user, phone='+375 (29) 123-45-67', birth_date='2020-01-01')
        with self.assertRaises(ValidationError):
            c.full_clean()


class SaleTest(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='buyer', password='pass')
        self.customer = Customer.objects.create(user=user, phone='+375 (29) 123-45-67', birth_date='1990-01-01')
        self.product = Product.objects.create(article='P001', name='Product', price=100.00, stock=10)
        supplier = Supplier.objects.create(name='Test', address='Addr', phone='+375 (29) 123-45-67')
        Supply.objects.create(product=self.product, supplier=supplier, quantity=10, purchase_date='2024-01-01')
    
    def test_create_sale(self):
        sale = Sale.objects.create(customer=self.customer)
        self.assertIsNotNone(sale.id)
    
    def test_sale_total(self):
        sale = Sale.objects.create(customer=self.customer)
        SaleItem.objects.create(sale=sale, product=self.product, quantity=2, unit_price=self.product.price)
        sale.calculate_total()
        self.assertEqual(sale.total_amount, 200.00)
    
    def test_sale_item_properties(self):
        sale = Sale.objects.create(customer=self.customer)
        item = SaleItem.objects.create(sale=sale, product=self.product, quantity=3, unit_price=self.product.price)
        self.assertEqual(item.unit_price, 100.00)
        self.assertEqual(item.total_price, 300.00)


class SupplierTest(TestCase):
    def test_create(self):
        s = Supplier.objects.create(name='Test Supplier', address='Address', phone='+375 (29) 123-45-67')
        self.assertEqual(str(s), 'Test Supplier')


class SupplyTest(TestCase):
    def setUp(self):
        self.supplier = Supplier.objects.create(name='Supplier', address='Addr', phone='+375 (29) 123-45-67')
        self.product = Product.objects.create(article='S001', name='Stock Product', price=50.00)
    
    def test_create(self):
        supply = Supply.objects.create(product=self.product, supplier=self.supplier, quantity=10, purchase_date='2024-01-01', purchase_price=30.00)
        self.assertEqual(supply.quantity, 10)