from django.db import models

class FAQItem(models.Model):
    """Вопрос-ответ"""
    question = models.CharField(max_length=300, verbose_name='Вопрос')
    answer = models.TextField(verbose_name='Ответ')
    date_added = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')
    is_published = models.BooleanField(default=True, verbose_name='Опубликовано')
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок сортировки')

    class Meta:
        verbose_name = 'Вопрос-ответ'
        verbose_name_plural = 'Вопросы-ответы'
        ordering = ['order', '-date_added']

    def __str__(self):
        return self.question
