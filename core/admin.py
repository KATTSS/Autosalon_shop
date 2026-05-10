from django.contrib import admin
from .models import CompanyInfo, Employee, PickupPoint

admin.site.register(CompanyInfo)
admin.site.register(Employee)
admin.site.register(PickupPoint)

