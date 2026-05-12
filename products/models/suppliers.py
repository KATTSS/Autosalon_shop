from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
import re

def validate_phone(value):
    """Валидация номера телефона в формате +375 (XX) XXX-XX-XX"""
    pattern = r'^\+375 ?\(\d{2}\) ?\d{3}-\d{2}-\d{2}$'
    if not re.match(pattern, value):
        raise ValidationError(
            'Номер телефона должен быть в формате: +375 (XX) XXX-XX-XX'
        )

class Supplier(models.Model):
    """Поставщик"""
    name = models.CharField(max_length=200, verbose_name='Название', unique=True)
    address = models.TextField(verbose_name='Адрес')
    phone = models.CharField(max_length=20, verbose_name='Телефон', validators=[validate_phone], help_text='+375 (XX) XXX-XX-XX')
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

    def display_supplies_count(self):
        """Количество поставок"""
        return self.supply_set.count()
    display_supplies_count.short_description = 'Поставок'