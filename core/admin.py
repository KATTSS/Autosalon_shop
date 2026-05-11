from django.contrib import admin
from .models import CompanyInfo, Employee, PickupPoint

@admin.register(CompanyInfo)
class CompanyInfoAdmin(admin.ModelAdmin):
    list_display = ('name', 'logo', 'history', 'requisites')
    list_filter = ('name',)

    def has_add_permission(self, request):
        if CompanyInfo.objects.exists():
            return False
        return True

@admin.register(Employee)
class EmplouyeeAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'position', 'phone', 'email','photo', 'description', 'user')
    list_filter = ('position', )
    fields = [('full_name', 'position', 'photo', 'user'), ('phone', 'email'), 'description']

@admin.register(PickupPoint)
class PickupPointAdmin(admin.ModelAdmin):
    list_display = ('address', 'working_hours', 'phone')
    list_filter = ('address', 'working_hours')
    fields = [('address', 'working_hours'), 'phone']