from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone

class PromoCode(models.Model):
    """Промокод / купон"""
    code = models.CharField(max_length=50, unique=True, verbose_name='Код')
    discount_percent = models.PositiveIntegerField(
        verbose_name='Скидка (%)',
        validators=[MinValueValidator(1)]
    )
    valid_from = models.DateTimeField(verbose_name='Действует с')
    valid_to = models.DateTimeField(verbose_name='Действует до')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    description = models.TextField(verbose_name='Описание', blank=True)

    class Meta:
        verbose_name = 'Промокод'
        verbose_name_plural = 'Промокоды'
        ordering = ['-valid_to']

    def __str__(self):
        return f'{self.code} — {self.discount_percent}%'

    def is_valid(self):
        """Проверка действительности промокода"""
        now = timezone.now()
        return self.is_active and self.valid_from <= now <= self.valid_to