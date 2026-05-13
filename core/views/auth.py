from django.views.generic import TemplateView, CreateView
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from dateutil.relativedelta import relativedelta
import re
import logging

logger = logging.getLogger(__name__)


class RegisterForm(UserCreationForm):
    """Расширенная форма регистрации"""
    
    email = forms.EmailField(
        required=True,
        label='Email',
        widget=forms.EmailInput(attrs={'placeholder': 'example@mail.ru'})
    )
    
    phone = forms.CharField(
        max_length=20,
        required=True,
        label='Телефон',
        widget=forms.TextInput(attrs={'placeholder': '+375 (29) XXX-XX-XX'}),
        help_text='Формат: +375 (XX) XXX-XX-XX'
    )
    
    birth_date = forms.DateField(
        required=True,
        label='Дата рождения',
        widget=forms.DateInput(attrs={'type': 'date'}),
        help_text='Вы должны быть старше 18 лет'
    )
    
    class Meta(UserCreationForm.Meta):
        fields = ['username', 'email', 'phone', 'birth_date', 'password1', 'password2']
    
    def clean_phone(self):
        """Валидация телефона"""
        phone = self.cleaned_data.get('phone')
        pattern = r'^\+375 \(\d{2}\) \d{3}-\d{2}-\d{2}$'
        if not re.match(pattern, phone):
            raise ValidationError(
                'Номер телефона должен быть в формате: +375 (XX) XXX-XX-XX\n'
                'Пример: +375 (29) 123-45-67'
            )
        return phone
    
    def clean_birth_date(self):
        """Валидация возраста 18+"""
        birth_date = self.cleaned_data.get('birth_date')
        if birth_date:
            today = timezone.now().date()
            age = relativedelta(today, birth_date).years
            if age < 18:
                raise ValidationError(
                    f'Вам должно быть не менее 18 лет. Ваш возраст: {age} лет.'
                )
        return birth_date


class LoginView(TemplateView):
    """Страница входа"""
    template_name = 'core/login.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from django.contrib.auth.forms import AuthenticationForm
        context['form'] = AuthenticationForm()
        return context
    
    def post(self, request, *args, **kwargs):
        from django.contrib.auth.forms import AuthenticationForm
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            logger.info(f'User {user.username} logged in')
            messages.success(request, f'Добро пожаловать, {user.username}!')
            next_url = request.GET.get('next', 'core:home')
            return redirect(next_url)
        
        messages.error(request, 'Неверное имя пользователя или пароль')
        logger.warning(f'Failed login attempt for {request.POST.get("username")}')
        return redirect('core:login')


class LogoutView(TemplateView):
    """Выход из системы"""
    template_name = 'core/logout.html'
    
    def get(self, request, *args, **kwargs):
        logout(request)
        messages.info(request, 'Вы вышли из системы')
        return redirect('core:home')


class RegisterView(CreateView):
    """Регистрация нового пользователя"""
    template_name = 'core/register.html'
    form_class = RegisterForm
    success_url = reverse_lazy('core:login')
    
    def form_valid(self, form):
        from products.models import Customer
        
        # Создаём пользователя
        user = form.save()
        
        # Создаём запись Customer с обязательными данными
        Customer.objects.create(
            user=user,
            phone=form.cleaned_data['phone'],
            birth_date=form.cleaned_data['birth_date']
        )
        
        messages.success(
            self.request, 
            f'Регистрация успешна, {user.username}! Теперь вы можете войти.'
        )
        return redirect(self.success_url)
    
    def form_invalid(self, form):
        messages.error(
            self.request,
            'Пожалуйста, исправьте ошибки в форме.'
        )
        return super().form_invalid(form)