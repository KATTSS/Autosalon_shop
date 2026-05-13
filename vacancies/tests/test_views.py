from django.test import TestCase
from django.urls import reverse


class VacanciesViewsTest(TestCase):
    def test_list(self):
        response = self.client.get(reverse('vacancies:list'))
        self.assertEqual(response.status_code, 200)