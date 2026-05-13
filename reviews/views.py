from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
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
        return Review.objects.filter(is_moderated=True).order_by('-created_date')


class ReviewCreateView(LoginRequiredMixin, CreateView):
    """Создание отзыва"""
    model = Review
    template_name = 'reviews/add.html'
    fields = ['text', 'rating', 'product']
    success_url = reverse_lazy('reviews:list')
    login_url = 'core:login'
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Отзыв отправлен на модерацию!')
        return super().form_valid(form)


class ReviewUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Редактирование отзыва (только своего)"""
    model = Review
    template_name = 'reviews/edit.html'
    fields = ['text', 'rating', 'product']
    success_url = reverse_lazy('reviews:list')
    login_url = 'core:login'
    
    def test_func(self):
        """Проверка, что пользователь — автор отзыва"""
        review = self.get_object()
        return review.user == self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, 'Отзыв обновлён!')
        return super().form_valid(form)


class ReviewDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Удаление отзыва (только своего)"""
    model = Review
    template_name = 'reviews/delete.html'
    success_url = reverse_lazy('reviews:list')
    login_url = 'core:login'
    
    def test_func(self):
        review = self.get_object()
        return review.user == self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, 'Отзыв удалён!')
        return super().form_valid(form)