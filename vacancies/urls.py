from django.urls import path, re_path
from . import views

app_name = 'vacancies'

urlpatterns = [
    path('', views.VacancyListView.as_view(), name='list'),
]