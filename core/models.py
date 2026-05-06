from django.db import models

from django.db import models


class CompanyInfo(models.Model):
    """О компании"""
    name = models.CharField(max_length=200, verbose_name='Название компании')
    logo = models.ImageField(upload_to='company/', verbose_name='Логотип', blank=True, null=True)
    history = models.TextField(verbose_name='История компании')
    requisites = models.TextField(verbose_name='Реквизиты')
    video_url = models.URLField(verbose_name='Ссылка на видео', blank=True, null=True)

    class Meta:
        verbose_name = 'Информация о компании'
        verbose_name_plural = 'Информация о компании'

    def __str__(self):
        return self.name


class Employee(models.Model):
    """Сотрудники (для страницы Контакты)"""
    full_name = models.CharField(max_length=200, verbose_name='ФИО')
    position = models.CharField(max_length=200, verbose_name='Должность')
    photo = models.ImageField(upload_to='employees/', verbose_name='Фото')
    description = models.TextField(verbose_name='Описание выполняемых работ')
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    email = models.EmailField(verbose_name='Email')
    user = models.OneToOneField(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Учётная запись',
        help_text='Связь с учётной записью сотрудника'
    )

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'

    def __str__(self):
        return f'{self.full_name} — {self.position}'


class PickupPoint(models.Model):
    """Точки самовывоза"""
    address = models.CharField(max_length=300, verbose_name='Адрес')
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    working_hours = models.CharField(max_length=200, verbose_name='Часы работы')
    description = models.TextField(verbose_name='Описание', blank=True)

    class Meta:
        verbose_name = 'Точка самовывоза'
        verbose_name_plural = 'Точки самовывоза'

    def __str__(self):
        return self.address