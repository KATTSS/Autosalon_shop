from django.db import models
from django.core.validators import MinValueValidator

class Sale(models.Model):
    """Продажа"""
    customer = models.ForeignKey(
        'Customer',
        on_delete=models.CASCADE,
        verbose_name='Покупатель'
    )
    sale_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата продажи')
    promo_code = models.ForeignKey(
        'promo.PromoCode',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Промокод'
    )
    pickup_point = models.ForeignKey(
        'core.PickupPoint',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Точка самовывоза'
    )
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Общая стоимость',
        default=0
    )

    class Meta:
        verbose_name = 'Продажа'
        verbose_name_plural = 'Продажи'
        ordering = ['-sale_date']

    def __str__(self):
        return f'Продажа №{self.id} — {self.customer} ({self.sale_date.strftime("%d.%m.%Y")})'

    def calculate_total(self):
        """Расчёт стоимости продажи"""
        total = sum(item.total_price for item in self.items.all())
        if self.promo_code and self.promo_code.is_valid():
            total *= (1 - self.promo_code.discount_percent / 100)
        self.total_amount = total
        self.save()


class SaleItem(models.Model):
    """Проданный товар"""
    sale = models.ForeignKey(
        Sale,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Продажа'
    )
    product = models.ForeignKey(
        'Product',
        on_delete=models.CASCADE,
        verbose_name='Товар'
    )
    quantity = models.PositiveIntegerField(verbose_name='Количество', validators=[MinValueValidator(1)])

    class Meta:
        verbose_name = 'Проданный товар'
        verbose_name_plural = 'Проданные товары'

    def __str__(self):
        return f'{self.product.name} x{self.quantity}'

    @property
    def unit_price(self):
        """Цена за единицу из товара"""
        return self.product.price

    @property
    def total_price(self):
        """Цена проданного товара"""
        return self.quantity * self.product.price

    def save(self, *args, **kwargs):
        """Сохранение данных о проданном товаре"""
        if self.pk is None:
            if self.product.stock >= self.quantity:
                self.product.stock -= self.quantity
                self.product.save()
            else:
                raise ValueError(f'Недостаточно товара "{self.product.name}" на складе!')
        super().save(*args, **kwargs)
        self.sale.calculate_total()