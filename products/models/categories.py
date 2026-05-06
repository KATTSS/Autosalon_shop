from django.db import models

class ProductType(models.Model):
    """Тип товара"""
    name = models.CharField(max_length=200, verbose_name='Название категории')
    description = models.TextField(verbose_name='Описание', blank=True)

    class Meta:
        verbose_name = 'Тип товара'
        verbose_name_plural = 'Типы товаров'

    def __str__(self):
        return self.name