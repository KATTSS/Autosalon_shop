from django.contrib import admin
from .models import CompanyInfo, Employee, PickupPoint

@admin.register(CompanyInfo)
class CompanyInfoAdmin(admin.ModelAdmin):
    list_display = ('name', 'logo', 'history', 'requisites')

@admin.register(Employee)
class EmplouyeeAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'position', 'phone', 'email','photo', 'description', 'user')

@admin.register(PickupPoint)
class PickupPointAdmin(admin.ModelAdmin):
    list_display = ('address', 'working_hours', 'phone', 'description')