from django.views.generic import ListView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Review


class ReviewListView(ListView):
    model = Review
    template_name = 'reviews/list.html'
    context_object_name = 'reviews'
    paginate_by = 20
    
    def get_queryset(self):
        return Review.objects.filter(is_moderated=True).order_by('-created_date')


@login_required(login_url='core:login')
def review_create(request):
    if request.method == 'POST':
        text = request.POST.get('text', '')
        rating = request.POST.get('rating', '')
        product_id = request.POST.get('product', '') or None
        
        if text and rating:
            Review.objects.create(
                user=request.user,
                text=text,
                rating=rating,
                product_id=product_id
            )
            messages.success(request, 'Отзыв отправлен на модерацию!')
            return redirect('reviews:list')
    
    from products.models import Product
    products = Product.objects.all()
    ratings = range(1, 6)
    return render(request, 'reviews/add.html', {'products': products, 'ratings': ratings})


class ReviewUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Review
    template_name = 'reviews/edit.html'
    fields = ['text', 'rating', 'product']
    success_url = reverse_lazy('reviews:list')
    login_url = 'core:login'
    
    def test_func(self):
        review = self.get_object()
        return review.user == self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, 'Отзыв обновлён!')
        return super().form_valid(form)


class ReviewDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
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