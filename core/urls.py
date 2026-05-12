from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Главная страница
    path('', views.HomeView.as_view(), name='home'),
    
    # О компании
    path('about/', views.AboutView.as_view(), name='about'),
    
    # Контакты
    path('contacts/', views.ContactsView.as_view(), name='contacts'),
    
    # Политика конфиденциальности
    path('privacy/', views.PrivacyView.as_view(), name='privacy'),
    
    # Каталог товаров
    path('catalog/', views.ProductListView.as_view(), name='catalog'),
    path('catalog/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    
    # Корзина
    path('cart/', views.CartView.as_view(), name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:product_id>/', views.update_cart, name='update_cart'),
    
    # Оформление заказа
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    
    # Личный кабинет
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/orders/', views.OrderHistoryView.as_view(), name='order_history'),
    
    # Авторизация
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
]