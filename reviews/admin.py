from django.contrib import admin
from .models import Review

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'rating', 'created_date', 'is_moderated', 'text_preview')
    list_filter = ('rating', 'created_date', 'product', 'is_moderated')
    search_fields = ('user__username', 'text', 'product__name')
    list_editable = ('is_moderated',)
    readonly_fields = ('created_date',)
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'product', 'rating')
        }),
        ('Содержание', {
            'fields': ('text',)
        }),
        ('Модерация', {
            'fields': ('is_moderated', 'created_date')
        }),
    )
    
    def text_preview(self, obj):
        """Превью текста для списка"""
        return obj.text[:100] + '...' if len(obj.text) > 100 else obj.text
    text_preview.short_description = 'Текст отзыва'