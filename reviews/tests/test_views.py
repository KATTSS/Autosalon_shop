from django.test import TestCase
from django.urls import reverse


class ReviewsViewsTest(TestCase):
    def test_list(self):
        response = self.client.get(reverse('reviews:list'))
        self.assertEqual(response.status_code, 200)
    
    def test_add_anonymous(self):
        response = self.client.get(reverse('reviews:add'))
        self.assertNotEqual(response.status_code, 200)