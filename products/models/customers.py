from django.db import models
from django.contrib.auth.models import User

class Customer(models.Model):
    """Покупатель"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    
    class Meta:
        verbose_name = 'Покупатель'
        verbose_name_plural = 'Покупатели'

    def __str__(self):
        return f'{self.user.get_full_name() or self.user.username}'

    def display_total_purchases(self):
        """Общее количество покупок"""
        return self.sale_set.count()
    display_total_purchases.short_description = 'Всего покупок'