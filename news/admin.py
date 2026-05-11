from django.contrib import admin
from .models import Article

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_published', 'published_date', 'updated_date', 'full_text', 'image')
    list_filter = ('updated_date',)


