from django.urls import path
from . import views

app_name = 'news'

urlpatterns = [
    # Список всех новостей
    path('', views.NewsListView.as_view(), name='list'),
    
    # Детальная новость (используем slug в URL)
    # Пример: /news/skidki-na-tovary/
    path('<slug:slug>/', views.NewsDetailView.as_view(), name='detail'),
    
    # Или по ID (альтернатива)
    # path('<int:pk>/', views.NewsDetailView.as_view(), name='detail'),
]