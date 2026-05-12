from django.contrib import admin
from django import forms
from django.utils import timezone
from .models import ProductType, Customer, Manufacturer, Product, Sale, SaleItem, Supplier, Supply


@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_filter = ('name',)


class SaleInline(admin.TabularInline):
    model = Sale
    extra = 0
    fields = ('sale_date', 'total_amount', 'pickup_point', 'promo_code')
    readonly_fields = ('sale_date', 'total_amount', 'pickup_point', 'promo_code')
    can_delete = False
    show_change_link = True
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'birth_date', 'age', 'display_total_purchases')
    list_filter = ('birth_date',)
    search_fields = ('user__username', 'phone')
    inlines = [SaleInline]
    
    def age(self, obj):
        return obj.age
    age.short_description = 'Возраст'

@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ('name', 'country')
    list_filter = ('country',)


class SupplyInline(admin.TabularInline):
    model = Supply
    extra = 1
    fields = ('supplier', 'quantity', 'purchase_date', 'purchase_price')
    

class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'

    def clean_article(self):
        article = self.cleaned_data.get('article')
        if article:
            existing = Product.objects.filter(article=article).first()
            if existing and existing.pk != self.instance.pk:
                self.instance.name = existing.name
                self.instance.price = existing.price
                self.instance.manufacturer = existing.manufacturer
                self.instance.product_type = existing.product_type
                self.instance.description = existing.description
                self.cleaned_data['name'] = existing.name
                self.cleaned_data['price'] = existing.price
                self.cleaned_data['manufacturer'] = existing.manufacturer
                self.cleaned_data['product_type'] = existing.product_type
                self.cleaned_data['description'] = existing.description
        return article


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    list_display = ('article', 'name', 'product_type', 'price', 'manufacturer', 'display_suppliers', 'stock', 'description')
    list_filter = ('product_type', 'manufacturer', 'suppliers', 'stock')
    inlines = [SupplyInline]
    readonly_fields = ('stock',)


class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 1
    fields = ('product', 'quantity', 'unit_price', 'total_price', 'discounted_total_price', 'discount_amount')
    readonly_fields = ('unit_price','total_price', 'discounted_total_price', 'discount_amount')
    
    def has_change_permission(self, request, obj=None):
        if obj and obj.sale_id:
            return False
        return True
    
    def has_delete_permission(self, request, obj=None):
        if obj and obj.sale_id:
            return False
        return True

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'sale_date_user', 'sale_date_utc', 
        'pickup_point', 'total_amount', 'discounted_total_amount',
        'promo_code', 'customer'
    )
    list_filter = ('sale_date', 'pickup_point', 'promo_code', 'customer')
    inlines = [SaleItemInline]
    readonly_fields = ('total_amount', 'discounted_total_amount', 'sale_date')
    
    def sale_date_user(self, obj):
        """Дата продажи в часовом поясе пользователя (UTC+3)"""
        tz = timezone.get_fixed_timezone(180)
        user_time = obj.sale_date.astimezone(tz)
        return user_time.strftime('%d/%m/%Y %H:%M:%S')
    sale_date_user.short_description = 'Дата продажи (МСК)'
    
    def sale_date_utc(self, obj):
        """Дата продажи в UTC"""
        return obj.sale_date.strftime('%d/%m/%Y %H:%M:%S')
    sale_date_utc.short_description = 'Дата продажи (UTC)'


    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            instance.save()
        formset.save_m2m()
        if form.instance.pk:
            form.instance.calculate_total()

    def has_change_permission(self, request, obj=None):
        if obj:
            return False
        return True

@admin.register(SaleItem)
class SaleItemAdmin(admin.ModelAdmin):
    list_display = (
        'product', 'sale', 'quantity', 'unit_price', 
        'total_price', 'discounted_total_price', 'discount_amount'
    )
    list_filter = ('product', 'sale__sale_date')
    readonly_fields = (
        'product', 'sale', 'quantity', 'unit_price', 
        'total_price', 'discounted_total_price', 'discount_amount'
    )
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


class SupplierSupplyInline(admin.TabularInline):
    model = Supply
    extra = 1
    fields = ('product', 'quantity', 'purchase_price', 'purchase_date')


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'phone', 'email', 'display_supplies_count')
    list_filter = ('name', 'address')
    inlines = [SupplierSupplyInline]


@admin.register(Supply)
class SupplyAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', 'purchase_date', 'purchase_price', 'supplier')
    list_filter = ('product', 'supplier', 'purchase_date', 'quantity')

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['purchase_price'].widget.attrs.update({
            'min': '0',
            'step': '0.01'
        })
        form.base_fields['quantity'].widget.attrs.update({'min': '1'})
        return form