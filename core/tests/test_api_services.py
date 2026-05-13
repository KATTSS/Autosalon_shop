from unittest.mock import patch, Mock
from django.test import TestCase
from core.services.api_services import get_currency_rates, get_weather


class CurrencyRatesTest(TestCase):
    @patch('core.services.api_services.requests.get')
    def test_success(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {'Cur_Abbreviation': 'USD', 'Cur_Name': 'Доллар', 'Cur_OfficialRate': 3.25, 'Cur_Scale': 1, 'Date': '2024-01-01'},
            {'Cur_Abbreviation': 'EUR', 'Cur_Name': 'Евро', 'Cur_OfficialRate': 3.55, 'Cur_Scale': 1, 'Date': '2024-01-01'},
            {'Cur_Abbreviation': 'JPY', 'Cur_Name': 'Иена', 'Cur_OfficialRate': 2.00, 'Cur_Scale': 100, 'Date': '2024-01-01'},
        ]
        mock_get.return_value = mock_response
        result = get_currency_rates()
        self.assertIn('USD', result)
        self.assertIn('EUR', result)
        self.assertNotIn('JPY', result)
        self.assertEqual(result['USD']['rate'], 3.25)
    
    @patch('core.services.api_services.requests.get')
    def test_bad_status(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        result = get_currency_rates()
        self.assertIsNone(result)
    
    @patch('core.services.api_services.requests.get')
    def test_exception(self, mock_get):
        mock_get.side_effect = Exception('Network error')
        result = get_currency_rates()
        self.assertIsNone(result)


class WeatherTest(TestCase):
    @patch('core.services.api_services.requests.get')
    def test_success(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'name': 'Minsk',
            'main': {'temp': 15.5, 'feels_like': 14.0, 'temp_min': 12.0, 'temp_max': 18.0, 'humidity': 60, 'pressure': 1013},
            'wind': {'speed': 3.5},
            'weather': [{'description': 'ясно', 'icon': '01d'}],
            'clouds': {'all': 20},
            'visibility': 10000,
        }
        mock_get.return_value = mock_response
        with self.settings(OPENWEATHER_API_KEY='test_key'):
            result = get_weather()
        self.assertEqual(result['city'], 'Minsk')
        self.assertEqual(result['temperature'], 16)
        self.assertEqual(result['humidity'], 60)
        self.assertEqual(result['description'], 'Ясно')
    
    def test_no_api_key(self):
        with self.settings(OPENWEATHER_API_KEY='ваш_ключ_сюда'):
            result = get_weather()
        self.assertIsNone(result)
    
    @patch('core.services.api_services.requests.get')
    def test_exception(self, mock_get):
        mock_get.side_effect = Exception('Network error')
        with self.settings(OPENWEATHER_API_KEY='test_key'):
            result = get_weather()
        self.assertIsNone(result)