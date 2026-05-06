from django.db import models
from django.urls import reverse

class Article(models.Model):
    """Новости и статьи"""
    title = models.CharField(max_length=250, verbose_name='Заголовок')
    slug = models.SlugField(max_length=250, unique=True, verbose_name='ЧПУ')
    short_text = models.TextField(verbose_name='Краткое содержание (одно предложение)')
    full_text = models.TextField(verbose_name='Полный текст статьи')
    image = models.ImageField(upload_to='news/', verbose_name='Картинка')
    published_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')
    updated_date = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    is_published = models.BooleanField(default=True, verbose_name='Опубликовано')

    class Meta:
        verbose_name = 'Статья'
        verbose_name_plural = 'Статьи'
        ordering = ['-published_date']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('news_detail', kwargs={'slug': self.slug})
