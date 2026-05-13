from django import template
from django.utils import timezone
import pytz
import calendar 

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
    
    year = user_now.year
    month = user_now.month
    days_in_month = calendar.monthrange(year, month)[1]
    
    first_day = user_now.replace(day=1)
    first_weekday = first_day.weekday()  
    
    months_ru = [
        'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
        'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
    ]
    
    col_width = 4
    sep = "+" + "-" * col_width + "+" + "-" * col_width + "+" + "-" * col_width + "+" + "-" * col_width + "+" + "-" * col_width + "+" + "-" * col_width + "+" + "-" * col_width + "+"
    
    lines = []
    lines.append(f"Текущий месяц: {months_ru[month - 1]} {year}")
    lines.append(sep)
    lines.append(f"|{'ПН':^{col_width}}|{'ВТ':^{col_width}}|{'СР':^{col_width}}|{'ЧТ':^{col_width}}|{'ПТ':^{col_width}}|{'СБ':^{col_width}}|{'ВС':^{col_width}}|")
    lines.append(sep)
    
    day = 1
    for week in range(6):
        row = "|"
        for weekday in range(7):
            if week == 0 and weekday < first_weekday:
                row += f"{' ':^{col_width}}|"
            elif day <= days_in_month:
                if day == user_now.day:
                    row += f"[{day:2d}]|"
                else:
                    row += f"{day:2d}  |"
                day += 1
            else:
                row += f"{' ':^{col_width}}|"
        lines.append(row)
        if day > days_in_month:
            break
        lines.append(sep)
    
    lines.append(f"Сегодня: {user_now.strftime('%d/%m/%Y')} (UTC: {now.strftime('%d/%m/%Y')})")
    
    return '\n'.join(lines)