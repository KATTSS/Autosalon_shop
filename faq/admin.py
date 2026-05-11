from django.contrib import admin
from .models import FAQItem

@admin.register(FAQItem)
class FAQItemAdmin(admin.ModelAdmin):
    list_display = ('question', 'order', 'answer_preview', 'is_published', 'date_added')
    list_display_links = ('question',)  
    list_editable = ('order', 'is_published')
    list_filter = ('is_published', 'date_added')
    search_fields = ('question', 'answer')
    ordering = ['order', '-date_added']
    
    def answer_preview(self, obj):
        return obj.answer[:100] + '...' if len(obj.answer) > 100 else obj.answer
    answer_preview.short_description = 'Ответ (превью)'