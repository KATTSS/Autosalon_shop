import pytz
from django.utils import timezone

class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tzname = request.session.get('user_timezone', 'Europe/Minsk')
        
        try:
            timezone.activate(pytz.timezone(tzname))
        except pytz.UnknownTimeZoneError:
            timezone.deactivate()
        
        request.user_timezone = tzname
        
        response = self.get_response(request)
        return response