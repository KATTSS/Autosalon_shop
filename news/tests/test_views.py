from django.test import TestCase
from django.urls import reverse


class NewsViewsTest(TestCase):
    def test_list(self):
        response = self.client.get(reverse('news:list'))
        self.assertEqual(response.status_code, 200)