from django.urls import path
from . import views

app_name = 'vacancies'

urlpatterns = [
    # Список вакансий
    path('', views.VacancyListView.as_view(), name='list'),
    
    # Детальная вакансия
    path('<int:pk>/', views.VacancyDetailView.as_view(), name='detail'),
]