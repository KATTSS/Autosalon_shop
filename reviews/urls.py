from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    # Список отзывов
    path('', views.ReviewListView.as_view(), name='list'),
    
    # Добавить отзыв (только для авторизованных)
    path('add/', views.ReviewCreateView.as_view(), name='add'),
    
    # Мои отзывы (личный кабинет)
    # path('my/', views.MyReviewsView.as_view(), name='my'),
]