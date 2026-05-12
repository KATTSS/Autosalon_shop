from django import template
from django.utils import timezone
import pytz
from datetime import datetime

register = template.Library()

@register.simple_tag(takes_context=True)
def current_time_user(context):
    """Текущая дата и время в тайм-зоне пользователя"""
    request = context.get('request')
    if request and hasattr(request, 'session'):
        user_tz = request.session.get('user_timezone', 'Europe/Minsk')
    else:
        user_tz = 'Europe/Minsk'
    
    tz = pytz.timezone(user_tz)
    user_time = timezone.now().astimezone(tz)
    return user_time.strftime('%d/%m/%Y %H:%M:%S')

@register.simple_tag
def current_time_utc():
    """Текущая дата и время в UTC"""
    return timezone.now().strftime('%d/%m/%Y %H:%M:%S')

@register.filter
def format_date(value, tz_name='Europe/Minsk'):
    """Форматирование даты в указанной тайм-зоне"""
    if value is None:
        return ''
    
    if timezone.is_naive(value):
        value = timezone.make_aware(value, timezone.utc)
    
    tz = pytz.timezone(tz_name)
    value_tz = value.astimezone(tz)
    return value_tz.strftime('%d/%m/%Y %H:%M:%S')

@register.filter
def format_date_utc(value):
    """Форматирование даты в UTC"""
    if value is None:
        return ''
    
    if timezone.is_naive(value):
        value = timezone.make_aware(value, timezone.utc)
    
    value_utc = value.astimezone(pytz.UTC)
    return value_utc.strftime('%d/%m/%Y %H:%M:%S')

@register.simple_tag(takes_context=True)
def text_calendar(context):
    """Текстовый календарь с датами"""
    request = context.get('request')
    user_tz = request.session.get('user_timezone', 'Europe/Minsk') if request else 'Europe/Minsk'
    
    now = timezone.now()
    tz = pytz.timezone(user_tz)
    user_now = now.astimezone(tz)
    
    result = f"""
    Текущий месяц: {user_now.strftime('%B %Y')}
    ┌──────┬──────┬──────┬──────┬──────┬──────┬──────┐
    │ ПН   │ ВТ   │ СР   │ ЧТ   │ ПТ   │ СБ   │ ВС   │
    ├──────┼──────┼──────┼──────┼──────┼──────┼──────┤
    """
    
    # Получаем первый день месяца
    first_day = user_now.replace(day=1)
    # Получаем день недели первого дня (0 = ПН, 6 = ВС)
    first_weekday = first_day.weekday()
    
    # Добавляем пустые ячейки для дней до начала месяца
    day = 1
    days_in_month = 31  # упрощённо
    while first_day.month == user_now.month:
        first_day = first_day.replace(day=day)
        if first_day.month != user_now.month:
            break
        days_in_month = day
        day += 1
    
    day = 1
    for week in range(6):
        result += "│"
        for weekday in range(7):
            if week == 0 and weekday < first_weekday:
                result += "      │"
            elif day <= days_in_month:
                if day == user_now.day:
                    result += f" [{day:2d}]  │"
                else:
                    result += f"  {day:2d}   │"
                day += 1
            else:
                result += "      │"
        result += "\n"
        if day > days_in_month:
            break
        if week < 4:
            result += "├──────┼──────┼──────┼──────┼──────┼──────┼──────┤\n"
    
    result += "└──────┴──────┴──────┴──────┴──────┴──────┴──────┘"
    result += f"\nСегодня: {user_now.strftime('%d/%m/%Y')} (UTC: {now.strftime('%d/%m/%Y')})"
    
    return result