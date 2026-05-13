from django.urls import path, re_path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('', views.ReviewListView.as_view(), name='list'),
    path('add/', views.ReviewCreateView.as_view(), name='add'),
    re_path(r'^(?P<pk>\d+)/edit/$', views.ReviewUpdateView.as_view(), name='edit'),
    re_path(r'^(?P<pk>\d+)/delete/$', views.ReviewDeleteView.as_view(), name='delete'),
]