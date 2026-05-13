from django.urls import path, re_path
from . import views

app_name = 'news'

urlpatterns = [
    path('', views.NewsListView.as_view(), name='list'),
    re_path(r'^(?P<slug>[-\w]+)/$', views.NewsDetailView.as_view(), name='detail'),
    # path('<slug:slug>/', views.NewsDetailView.as_view(), name='detail'),
]