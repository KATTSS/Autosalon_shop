from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Sum, Count, Avg, Q
from django.db.models.functions import Length
from products.models import Sale, SaleItem, Product, ProductType, Customer
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from statistics import median, mode
from decimal import Decimal
from collections import Counter


class StatisticsView(UserPassesTestMixin, TemplateView):
    """Страница статистики (только для superuser)"""
    template_name = 'core/statistics.html'
    
    def test_func(self):
        return self.request.user.is_superuser
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['products_sorted'] = Product.objects.order_by('name')
        

        total_sales = Sale.objects.aggregate(
            total=Sum('total_amount'),
            total_discounted=Sum('discounted_total_amount'),
            count=Count('id')
        )
        context['total_sales'] = total_sales['total'] or 0
        context['total_discounted_sales'] = total_sales['total_discounted'] or 0
        context['total_sales_count'] = total_sales['count'] or 0
        

        sale_amounts = list(Sale.objects.values_list('total_amount', flat=True))
        if sale_amounts:
            context['avg_sale'] = sum(sale_amounts) / len(sale_amounts)

            sorted_amounts = sorted(sale_amounts)
            n = len(sorted_amounts)
            if n % 2 == 0:
                context['median_sale'] = (sorted_amounts[n//2 - 1] + sorted_amounts[n//2]) / 2
            else:
                context['median_sale'] = sorted_amounts[n//2]

            amount_counter = Counter(sale_amounts)
            most_common = amount_counter.most_common(1)
            context['mode_sale'] = most_common[0][0] if most_common else 0
        else:
            context['avg_sale'] = 0
            context['median_sale'] = 0
            context['mode_sale'] = 0
        
        today = timezone.now().date()
        ages = []
        for customer in Customer.objects.filter(birth_date__isnull=False):
            age = relativedelta(today, customer.birth_date).years
            ages.append(age)
        
        if ages:
            context['avg_age'] = sum(ages) / len(ages)
            sorted_ages = sorted(ages)
            n = len(sorted_ages)
            if n % 2 == 0:
                context['median_age'] = (sorted_ages[n//2 - 1] + sorted_ages[n//2]) / 2
            else:
                context['median_age'] = sorted_ages[n//2]
            context['min_age'] = min(ages)
            context['max_age'] = max(ages)
            context['total_customers_with_age'] = len(ages)
        else:
            context['avg_age'] = 0
            context['median_age'] = 0
            context['min_age'] = 0
            context['max_age'] = 0
            context['total_customers_with_age'] = 0
        
        popular_types = ProductType.objects.annotate(
            total_sold=Sum('product__saleitem__quantity')
        ).order_by('-total_sold')
        context['popular_types'] = popular_types[:5]
        context['most_popular_type'] = popular_types.first()
        
        profitable_types = ProductType.objects.annotate(
            total_revenue=Sum('product__saleitem__quantity') * 
                          Sum('product__price')
        ).order_by('-total_revenue')
        context['profitable_types'] = profitable_types[:5]
        context['most_profitable_type'] = profitable_types.first()
        
        top_products = Product.objects.annotate(
            total_sold=Sum('saleitem__quantity'),
            revenue=Sum('saleitem__quantity') * Sum('saleitem__unit_price')
        ).filter(total_sold__isnull=False).order_by('-total_sold')[:10]
        context['top_products'] = top_products
        
        context['total_products'] = Product.objects.count()
        context['total_customers'] = Customer.objects.count()
        context['total_reviews'] = Sale.objects.count()
        
        return context