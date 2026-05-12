from django.urls import path
from . import views

app_name = 'promo'

urlpatterns = [
    # Список промокодов
    path('', views.PromoListView.as_view(), name='list'),
    
    # Проверка промокода (AJAX)
    path('check/', views.check_promo, name='check'),
]