from django.db import models
from .manufacturers import Manufacturer
from .categories import ProductType
from .suppliers import Supplier

class Product(models.Model):
    """Товар"""
    article = models.CharField(max_length=50, unique=True, verbose_name='Артикул')
    name = models.CharField(max_length=250, verbose_name='Название')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
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