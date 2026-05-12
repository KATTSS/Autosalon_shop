from django.views.generic import TemplateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from products.models import Sale
from core.models import Customer


class ProfileView(LoginRequiredMixin, TemplateView):
    """Личный кабинет"""
    template_name = 'core/profile.html'
    login_url = 'core:login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer = Customer.objects.filter(user=self.request.user).first()
        context['customer'] = customer
        
        if customer:
            context['total_orders'] = Sale.objects.filter(customer=customer).count()
            context['last_orders'] = Sale.objects.filter(
                customer=customer
            ).order_by('-sale_date')[:5]
        
        return context


class OrderHistoryView(LoginRequiredMixin, ListView):
    """История заказов"""
    template_name = 'core/order_history.html'
    context_object_name = 'orders'
    login_url = 'core:login'
    paginate_by = 10
    
    def get_queryset(self):
        customer = Customer.objects.filter(user=self.request.user).first()
        if customer:
            return Sale.objects.filter(
                customer=customer
            ).order_by('-sale_date')
        return Sale.objects.none()