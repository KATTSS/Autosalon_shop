from django.test import TestCase
from django.urls import reverse


class FAQViewsTest(TestCase):
    def test_list(self):
        response = self.client.get(reverse('faq:list'))
        self.assertEqual(response.status_code, 200)