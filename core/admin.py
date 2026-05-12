from django.contrib import admin
from django.utils import timezone
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
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'position', 'phone', 'email', 'birth_date', 'age', 'photo', 'description', 'user')
    list_filter = ('position', 'birth_date')
    search_fields = ('full_name', 'phone', 'email')
    fields = [('full_name', 'position', 'photo', 'user'), ('phone', 'email'), ('birth_date',), 'description']
    
    def age(self, obj):
        return obj.age
    age.short_description = 'Возраст'


@admin.register(PickupPoint)
class PickupPointAdmin(admin.ModelAdmin):
    list_display = ('address', 'working_hours', 'phone')
    list_filter = ('address', 'working_hours')
    fields = [('address', 'working_hours'), 'phone']