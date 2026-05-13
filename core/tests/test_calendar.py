from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.contrib.sessions.middleware import SessionMiddleware
from core.views.calendar import DateTimeDemoView, set_timezone


class DateTimeDemoViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
    
    def test_page_accessible(self):
        response = self.client.get(reverse('core:datetime_demo'))
        self.assertEqual(response.status_code, 200)
    
    def test_context_has_timezone(self):
        response = self.client.get(reverse('core:datetime_demo'))
        self.assertIn('user_tz', response.context)
        self.assertIn('utc_now', response.context)
        self.assertIn('user_now', response.context)


class SetTimezoneTest(TestCase):
    def test_post_valid_timezone(self):
        response = self.client.post(reverse('core:set_timezone'), {'timezone': 'UTC'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.session.get('user_timezone'), 'UTC')
    
    def test_post_invalid_timezone(self):
        response = self.client.post(reverse('core:set_timezone'), {'timezone': 'INVALID'})
        self.assertEqual(response.status_code, 302)
    
    def test_get_redirects(self):
        response = self.client.get(reverse('core:set_timezone'))
        self.assertEqual(response.status_code, 302)