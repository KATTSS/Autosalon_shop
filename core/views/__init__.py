from .home import HomeView, AboutView, PrivacyView
from .catalog import ProductListView, ProductDetailView
from .cart import CartView, add_to_cart, remove_from_cart, update_cart
from .checkout import CheckoutView
from .auth import LoginView, LogoutView, RegisterView
from .profile import ProfileView, OrderHistoryView, ProfileUpdateView
from .contacts import ContactsView
from .calendar import DateTimeDemoView, set_timezone 
from .statistics import StatisticsView