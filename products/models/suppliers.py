from django.db import models

class Supplier(models.Model):
    """Поставщик"""
    name = models.CharField(max_length=200, verbose_name='Название')
    address = models.TextField(verbose_name='Адрес')
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    email = models.EmailField(verbose_name='Email', blank=True)
    employee = models.ForeignKey(
        'core.Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Ответственный сотрудник'
    )

    class Meta:
        verbose_name = 'Поставщик'
        verbose_name_plural = 'Поставщики'

    def __str__(self):
        return self.name