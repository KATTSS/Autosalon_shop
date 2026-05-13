from django.views.generic import ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Review


class ReviewListView(ListView):
    """Список отзывов"""
    model = Review
    template_name = 'reviews/list.html'
    context_object_name = 'reviews'
    paginate_by = 20
    
    def get_queryset(self):
        return Review.objects.filter(
            is_moderated=True
        ).order_by('-created_date')


class ReviewCreateView(LoginRequiredMixin, CreateView):
    """Добавление отзыва"""
    model = Review
    template_name = 'reviews/add.html'
    fields = ['text', 'rating', 'product']
    success_url = reverse_lazy('reviews:list')
    login_url = 'core:login'
    
    def get_form(self, form_class=None):
        """Настраиваем форму"""
        form = super().get_form(form_class)
        form.fields['rating'].widget.attrs.update({
            'min': 1,
            'max': 5
        })
        return form
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(
            self.request, 
            'Спасибо за отзыв! Он появится на сайте после модерации.'
        )
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(
            self.request, 
            'Пожалуйста, исправьте ошибки в форме.'
        )
        return super().form_invalid(form)