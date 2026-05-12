from django.views.generic import ListView, DetailView
from django.db.models import Q
from products.models import Product, ProductType


class ProductListView(ListView):
    """Каталог товаров с фильтрацией и поиском"""
    model = Product
    template_name = 'core/catalog.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Product.objects.filter(stock__gt=0)
        
        # Поиск по названию или артикулу
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(name__icontains=q) | 
                Q(article__icontains=q)
            )
        
        # Фильтр по категории
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(product_type_id=category)
        
        # Фильтр по производителю
        manufacturer = self.request.GET.get('manufacturer')
        if manufacturer:
            queryset = queryset.filter(manufacturer_id=manufacturer)
        
        # Фильтр по цене
        price_min = self.request.GET.get('price_min')
        price_max = self.request.GET.get('price_max')
        if price_min:
            queryset = queryset.filter(price__gte=price_min)
        if price_max:
            queryset = queryset.filter(price__lte=price_max)
        
        # Сортировка
        sort = self.request.GET.get('sort', 'name')
        sort_options = {
            'price_asc': 'price',
            'price_desc': '-price',
            'name': 'name',
            'name_desc': '-name',
            'newest': '-id',
        }
        ordering = sort_options.get(sort, 'name')
        queryset = queryset.order_by(ordering)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем все категории для фильтра
        context['categories'] = ProductType.objects.all()
        # Сохраняем текущие параметры фильтрации
        context['current_filters'] = {
            'category': self.request.GET.get('category', ''),
            'manufacturer': self.request.GET.get('manufacturer', ''),
            'price_min': self.request.GET.get('price_min', ''),
            'price_max': self.request.GET.get('price_max', ''),
            'sort': self.request.GET.get('sort', 'name'),
            'q': self.request.GET.get('q', ''),
        }
        return context


class ProductDetailView(DetailView):
    """Детальная страница товара"""
    model = Product
    template_name = 'core/product_detail.html'
    context_object_name = 'product'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Похожие товары из той же категории
        product = self.get_object()
        if product.product_type:
            context['related_products'] = Product.objects.filter(
                product_type=product.product_type
            ).exclude(id=product.id)[:4]
        return context