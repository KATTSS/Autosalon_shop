from django.views.generic import ListView, DetailView
from .models import Article

class NewsListView(ListView):
    model = Article
    template_name = 'news/list.html'
    context_object_name = 'articles'
    queryset = Article.objects.filter(is_published=True)

class NewsDetailView(DetailView):
    model = Article
    template_name = 'news/detail.html'
    context_object_name = 'article'