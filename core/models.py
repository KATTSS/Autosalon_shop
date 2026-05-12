from django.db import models
from products.models.validator import UserValidatorMixin
from dateutil.relativedelta import relativedelta
from django.utils import timezone

class CompanyInfo(models.Model):
    """О компании"""
    name = models.CharField(max_length=200, verbose_name='Название компании')
    logo = models.ImageField(upload_to='company/', verbose_name='Логотип', blank=True, null=True)
    history = models.TextField(verbose_name='История компании')
    requisites = models.TextField(verbose_name='Реквизиты')
    
    class Meta:
        verbose_name = 'Информация о компании'
        verbose_name_plural = 'Информация о компании'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.pk and CompanyInfo.objects.exists():
            raise ValueError("Может существовать только одна компания. Редактируйте существующую.")
        super().save(*args, **kwargs)


class Employee(UserValidatorMixin, models.Model):
    """Сотрудники (для страницы Контакты)"""
    full_name = models.CharField(max_length=200, verbose_name='ФИО')
    position = models.CharField(max_length=200, verbose_name='Должность')
    photo = models.ImageField(upload_to='employees/', verbose_name='Фото')
    description = models.TextField(verbose_name='Описание выполняемых работ')
    phone = models.CharField(
        max_length=20, 
        verbose_name='Телефон',
        help_text='Формат: +375 (XX) XXX-XX-XX'
    )
    email = models.EmailField(verbose_name='Email')
    user = models.OneToOneField(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Учётная запись',
        help_text='Связь с учётной записью сотрудника'
    )
    birth_date = models.DateField(
        verbose_name='Дата рождения',
        null=True,
        blank=True,
        help_text='Сотрудник должен быть старше 18 лет'
    )

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'

    def __str__(self):
        return f'{self.full_name} — {self.position}'
    
    @property
    def age(self):
        """Возвращает возраст сотрудника"""
        if self.birth_date:
            return relativedelta(timezone.now().date(), self.birth_date).years
        return None
    
    def save(self, *args, **kwargs):
        """Вызываем валидацию перед сохранением"""
        self.full_clean()
        super().save(*args, **kwargs)

class PickupPoint(UserValidatorMixin, models.Model):
    """Точки самовывоза"""
    address = models.CharField(max_length=300, verbose_name='Адрес')
    phone = models.CharField(
        max_length=20, 
        verbose_name='Телефон',
        help_text='Формат: +375 (XX) XXX-XX-XX'
    )
    working_hours = models.CharField(max_length=200, verbose_name='Часы работы')
   
    class Meta:
        verbose_name = 'Точка самовывоза'
        verbose_name_plural = 'Точки самовывоза'

    def __str__(self):
        return self.address