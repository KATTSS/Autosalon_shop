from django.test import TestCase
from django.urls import reverse
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User


class AuthTest(TestCase):
    def test_login_post_valid(self):
        User.objects.create_user(username='test', password='pass12345')
        response = self.client.post(reverse('core:login'), {
            'username': 'test',
            'password': 'pass12345',
        })
        self.assertEqual(response.status_code, 302)
    
    def test_login_post_invalid(self):
        response = self.client.post(reverse('core:login'), {
            'username': 'fake',
            'password': 'wrong',
        })
        self.assertEqual(response.status_code, 302)
    
    def test_register_post(self):
        response = self.client.post(reverse('core:register'), {
            'username': 'newuser',
            'email': 'new@test.com',
            'phone': '+375 (29) 123-45-67',
            'birth_date': '1990-01-01',
            'password1': 'complexpass123',
            'password2': 'complexpass123',
        })
        self.assertEqual(response.status_code, 302)
    
    def test_logout(self):
        User.objects.create_user(username='test', password='pass12345')
        self.client.login(username='test', password='pass12345')
        response = self.client.get(reverse('core:logout'))
        self.assertEqual(response.status_code, 302)

class CoreViewsTest(TestCase):
    def test_home(self):
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)
    
    def test_catalog(self):
        response = self.client.get(reverse('core:catalog'))
        self.assertEqual(response.status_code, 200)
    
    def test_about(self):
        response = self.client.get(reverse('core:about'))
        self.assertEqual(response.status_code, 200)
    
    def test_contacts(self):
        response = self.client.get(reverse('core:contacts'))
        self.assertEqual(response.status_code, 200)
    
    def test_privacy(self):
        response = self.client.get(reverse('core:privacy'))
        self.assertEqual(response.status_code, 200)
    
    def test_login(self):
        response = self.client.get(reverse('core:login'))
        self.assertEqual(response.status_code, 200)
    
    def test_register(self):
        response = self.client.get(reverse('core:register'))
        self.assertEqual(response.status_code, 200)
    
    def test_cart(self):
        response = self.client.get(reverse('core:cart'))
        self.assertEqual(response.status_code, 200)
    
    def test_cart_empty(self):
        response = self.client.get(reverse('core:cart'))
        self.assertContains(response, 'Корзина')
    
    def test_statistics_anonymous(self):
        response = self.client.get(reverse('core:statistics'))
        self.assertNotEqual(response.status_code, 200)