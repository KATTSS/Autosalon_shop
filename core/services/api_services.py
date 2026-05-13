import requests
from django.conf import settings


def get_currency_rates():
    try:
        url = "https://api.nbrb.by/exrates/rates?periodicity=0"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            currencies = ['USD', 'EUR', 'RUB', 'PLN']
            rates = {}
            for item in data:
                if item['Cur_Abbreviation'] in currencies:
                    rates[item['Cur_Abbreviation']] = {
                        'name': item['Cur_Name'],
                        'rate': item['Cur_OfficialRate'],
                        'scale': item['Cur_Scale'],
                        'date': item['Date']
                    }
            return rates
        return None
    except Exception as e:
        return None


def get_weather():
    api_key = getattr(settings, 'OPENWEATHER_API_KEY', None)
    
    if not api_key or api_key == 'ваш_ключ_сюда':
        return None
    
    try:
        city = "Minsk"
        country_code = "BY"
        
        url = (
            f"https://api.openweathermap.org/data/2.5/weather"
            f"?q={city},{country_code}"
            f"&appid={api_key}"
            f"&units=metric"
            f"&lang=ru"
        )
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            return {
                'city': data.get('name', 'Minsk'),
                'temperature': round(data['main']['temp']),
                'feels_like': round(data['main']['feels_like']),
                'temp_min': round(data['main']['temp_min']),
                'temp_max': round(data['main']['temp_max']),
                'humidity': data['main']['humidity'],
                'pressure': round(data['main']['pressure'] * 0.75),
                'wind_speed': round(data['wind']['speed'], 1),
                'description': data['weather'][0]['description'].capitalize(),
                'icon': data['weather'][0]['icon'],
                'icon_url': f"https://openweathermap.org/img/wn/{data['weather'][0]['icon']}@2x.png",
                'clouds': data['clouds']['all'],
                'visibility': round(data.get('visibility', 0) / 1000, 1),
            }
        
        return None
    except Exception as e:
        return None