from django.db import models

class Vacancy(models.Model):
    """Вакансия"""
    title = models.CharField(max_length=200, verbose_name='Должность')
    description = models.TextField(verbose_name='Описание вакансии')
    requirements = models.TextField(verbose_name='Требования')
    conditions = models.TextField(verbose_name='Условия работы')
    salary = models.CharField(max_length=100, verbose_name='Заработная плата', blank=True)
    is_active = models.BooleanField(default=True, verbose_name='Активна')
    created_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Вакансия'
        verbose_name_plural = 'Вакансии'
        ordering = ['-created_date']

    def __str__(self):
        return self.title