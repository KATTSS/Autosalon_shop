from django.contrib import admin
from .models import PromoCode

@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_percent', 'is_active', 'valid_from', 'valid_to', 'description')
    list_filter = ('is_active', 'discount_percent', 'valid_from', 'valid_to')
    fields = [('code', 'is_active', 'discount_percent'), ('valid_from', 'valid_to'), 'description']