from django.views.generic import TemplateView, CreateView
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse_lazy


class LoginView(TemplateView):
    """Страница входа"""
    template_name = 'core/login.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = AuthenticationForm()
        return context
    
    def post(self, request, *args, **kwargs):
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.username}!')
            
            # Перенаправляем на запрошенную страницу или на главную
            next_url = request.GET.get('next', 'core:home')
            return redirect(next_url)
        
        messages.error(request, 'Неверное имя пользователя или пароль')
        return redirect('core:login')


class LogoutView(TemplateView):
    """Выход из системы"""
    template_name = 'core/logout.html'  # Не обязательно, сразу редиректим
    
    def get(self, request, *args, **kwargs):
        logout(request)
        messages.info(request, 'Вы вышли из системы')
        return redirect('core:home')


class RegisterView(CreateView):
    """Регистрация нового пользователя"""
    template_name = 'core/register.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('core:login')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request, 
            'Регистрация успешна! Теперь вы можете войти.'
        )
        return response