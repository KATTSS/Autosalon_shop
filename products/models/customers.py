from django.db import models
from django.contrib.auth.models import User
from .validator import UserValidatorMixin
from dateutil.relativedelta import relativedelta
from django.utils import timezone

class Customer(UserValidatorMixin, models.Model):
    """Покупатель"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    phone = models.CharField(
        max_length=20, 
        verbose_name='Телефон',
        help_text='Формат: +375 (XX) XXX-XX-XX'
    )
    birth_date = models.DateField(
        verbose_name='Дата рождения',
        null=True,
        blank=True,
        help_text='Покупатель должен быть старше 18 лет'
    )
    
    class Meta:
        verbose_name = 'Покупатель'
        verbose_name_plural = 'Покупатели'

    def __str__(self):
        return f'{self.user.get_full_name() or self.user.username}'

    def display_total_purchases(self):
        """Общее количество покупок"""
        return self.sale_set.count()
    display_total_purchases.short_description = 'Всего покупок'
    
    @property
    def age(self):
        """Возвращает возраст покупателя"""
        if self.birth_date:
            return relativedelta(timezone.now().date(), self.birth_date).years
        return None
    
    def save(self, *args, **kwargs):
        """Вызываем валидацию перед сохранением"""
        self.full_clean()
        super().save(*args, **kwargs)