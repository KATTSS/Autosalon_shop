from django.views.generic import TemplateView, ListView, DetailView, UpdateView 
from django.contrib.auth.mixins import LoginRequiredMixin
from products.models import Sale, Customer
from django.urls import reverse_lazy 
from django.contrib import messages

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for order in context['orders']:
            order.discount = order.total_amount - order.discounted_total_amount
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование профиля"""
    model = Customer
    template_name = 'core/profile_edit.html'
    fields = ['phone', 'birth_date']
    success_url = reverse_lazy('core:profile')
    login_url = 'core:login'
    
    def get_object(self, queryset=None):
        customer, created = Customer.objects.get_or_create(
            user=self.request.user,
            defaults={'phone': '', 'birth_date': None}
        )
        return customer
    
    def form_valid(self, form):
        messages.success(self.request, 'Профиль успешно обновлён!')
        return super().form_valid(form)