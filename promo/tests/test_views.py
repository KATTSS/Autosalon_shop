from django.test import TestCase
from django.urls import reverse


class PromoViewsTest(TestCase):
    def test_list(self):
        response = self.client.get(reverse('promo:list'))
        self.assertEqual(response.status_code, 200)