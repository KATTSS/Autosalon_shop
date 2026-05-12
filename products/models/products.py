from django.db import models
from django.core.validators import MinValueValidator
from .manufacturers import Manufacturer
from .categories import ProductType
from .suppliers import Supplier

class Product(models.Model):
    """Товар"""
    article = models.CharField(max_length=50, verbose_name='Артикул', unique=True)
    name = models.CharField(max_length=250, verbose_name='Название')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена', validators=[MinValueValidator(0.0)])
    manufacturer = models.ForeignKey(
        Manufacturer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Изготовитель'
    )
    product_type = models.ForeignKey(
        ProductType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Тип товара'
    )
    description = models.TextField(verbose_name='Описание', blank=True)
    stock = models.PositiveIntegerField(default=0, verbose_name='Остаток на складе')
    suppliers = models.ManyToManyField(
        Supplier,
        through='Supply',
        verbose_name='Поставщики'
    )

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def __str__(self):
        return f'{self.article} — {self.name}'

    def display_suppliers(self):
        """Отображение поставщиков в админке"""
        return ', '.join([s.name for s in self.suppliers.all()[:3]])
    display_suppliers.short_description = 'Поставщики'

    def calculate_stock(self):
        """Расчет остатка на складе на основе поставок и продаж"""
        from django.db.models import Sum
        from .supplies import Supply
        from .sales import SaleItem
        
        
        total_supplied = Supply.objects.filter(
            product=self
        ).aggregate(
            total=Sum('quantity')
        )['total'] or 0
        
        
        total_sold = SaleItem.objects.filter(
            product=self
        ).aggregate(
            total=Sum('quantity')
        )['total'] or 0
        
        return total_supplied - total_sold
    
    def save(self, *args, **kwargs):
        """Переопределяем save для автоматического расчета stock"""
        if self.pk:
            
            self.stock = self.calculate_stock()
        super().save(*args, **kwargs)