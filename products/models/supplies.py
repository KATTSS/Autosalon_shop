from django.db import models

class Supply(models.Model):
    """Поставка"""
    product = models.ForeignKey(
        'Product',
        on_delete=models.CASCADE,
        verbose_name='Товар'
    )
    supplier = models.ForeignKey(
        'Supplier',
        on_delete=models.CASCADE,
        verbose_name='Поставщик'
    )
    quantity = models.PositiveIntegerField(verbose_name='Количество')
    purchase_date = models.DateField(verbose_name='Дата покупки')
    purchase_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Цена закупки',
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'Поставка'
        verbose_name_plural = 'Поставки'

    def __str__(self):
        return f'{self.product.name} от {self.supplier.name} — {self.quantity} шт. ({self.purchase_date})'

    def save(self, *args, **kwargs):
        """Сохранение данных о поставке"""
        if self.pk is None:
            self.product.stock += self.quantity
            self.product.save()
        super().save(*args, **kwargs)