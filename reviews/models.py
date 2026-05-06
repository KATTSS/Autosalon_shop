from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Review(models.Model):
    """Отзыв"""
    user = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    text = models.TextField(verbose_name='Текст отзыва')
    rating = models.PositiveIntegerField(
        verbose_name='Оценка',
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    created_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')
    is_moderated = models.BooleanField(default=False, verbose_name='Промодерирован')

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-created_date']

    def __str__(self):
        return f'Отзыв от {self.user.username} — {self.rating}/5'