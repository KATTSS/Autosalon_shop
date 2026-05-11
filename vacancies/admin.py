from django.contrib import admin
from .models import Vacancy

@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'created_date', 'salary', 'conditions', 'requirements', 'description')
    list_filter = ('is_active', 'created_date')
    fields = [('title', 'salary'), 'requirements', 'conditions', 'description']