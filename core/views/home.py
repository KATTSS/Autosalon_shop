from django.views.generic import TemplateView
from news.models import Article
from products.models import Product
from core.models import CompanyInfo


class HomeView(TemplateView):
    """Главная страница с последней новостью"""
    template_name = 'core/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['latest_article'] = Article.objects.filter(
            is_published=True
        ).first()
        context['featured_products'] = Product.objects.filter(
            stock__gt=0
        )[:6]
        return context


class AboutView(TemplateView):
    """Страница О компании"""
    template_name = 'core/about.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['company'] = CompanyInfo.objects.first()
        return context


class PrivacyView(TemplateView):
    """Политика конфиденциальности"""
    template_name = 'core/privacy.html'