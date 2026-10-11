from unittest.mock import patch
from django.test import SimpleTestCase
from core.services.api_services import get_currency_rates, get_weather


class CurrencyRatesTest(SimpleTestCase):
    
    
    @patch('core.services.api_services.requests.get')
    def test_exception(self, mock_get):
        mock_get.side_effect = Exception('Network error')
        result = get_currency_rates()
        self.assertIsNone(result)


class WeatherTest(SimpleTestCase):
    
    def test_no_api_key(self):
        with self.settings(OPENWEATHER_API_KEY='ваш_ключ_сюда'):
            result = get_weather()
        self.assertIsNone(result)
