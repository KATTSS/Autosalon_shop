from django.contrib import admin
from .models import ProductType, Customer, Manufacturer, Product, Sale, SaleItem, Supplier, Supply

admin.site.register(ProductType)
admin.site.register(Customer)
admin.site.register(Manufacturer)
admin.site.register(Product)
admin.site.register(Sale)
admin.site.register(SaleItem)
admin.site.register(Supplier)
admin.site.register(Supply)