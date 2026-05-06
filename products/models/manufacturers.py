from django.db import models

class Manufacturer(models.Model):
    """Изготовитель"""
    name = models.CharField(max_length=200, verbose_name='Название')
    country = models.CharField(max_length=100, verbose_name='Страна', blank=True)

    class Meta:
        verbose_name = 'Изготовитель'
        verbose_name_plural = 'Изготовители'

    def __str__(self):
        return self.name