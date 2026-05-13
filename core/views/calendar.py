from django.views.generic import TemplateView
from django.utils import timezone
from django.shortcuts import redirect
from django.contrib import messages
from core.services.api_services import get_currency_rates, get_weather
import pytz

def set_timezone(request):
    """Установка тайм-зоны пользователя"""
    if request.method == 'POST':
        tzname = request.POST.get('timezone', 'Europe/Minsk')
        
        try:
            pytz.timezone(tzname)
            request.session['user_timezone'] = tzname
            messages.success(request, f'Тайм-зона изменена на {tzname}')
        except pytz.UnknownTimeZoneError:
            messages.error(request, f'Неизвестная тайм-зона: {tzname}')
    
    return redirect('core:datetime_demo')


class DateTimeDemoView(TemplateView):
    """Демонстрационная страница дат"""
    template_name = 'core/datetime_demo.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        
        context['utc_now'] = now
        
        user_tz = self.request.session.get('user_timezone', 'Europe/Minsk')
        tz = pytz.timezone(user_tz)
        context['user_now'] = now.astimezone(tz)
        context['user_tz'] = user_tz
        
        from news.models import Article
        from reviews.models import Review
        
        context['latest_article'] = Article.objects.first()
        context['latest_review'] = Review.objects.first()
        
        currency_rates = get_currency_rates()
        weather = get_weather()
        
        print("Currency rates:", currency_rates)
        print("Weather:", weather)
        
        context['currency_rates'] = currency_rates
        context['weather'] = weather
        
        return context