from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.core.exceptions import ValidationError

class PromoCode(models.Model):
    """Промокод / купон"""
    code = models.CharField(max_length=50, unique=True, verbose_name='Код')
    discount_percent = models.PositiveIntegerField(
        verbose_name='Скидка (%)',
        validators=[MinValueValidator(1), MaxValueValidator(100)]
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

    def clean(self):
        """Валидация: дата окончания не может быть раньше даты начала"""
        if self.valid_from and self.valid_to:
            if self.valid_to < self.valid_from:
                raise ValidationError({
                    'valid_to': 'Дата окончания не может быть раньше даты начала действия промокода.'
                })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)