"""
تست محافظت صفحات ادمین و داشبورد
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse


class AdminSecurityTests(TestCase):
    """تست‌های محافظت صفحات ادمین"""
    
    def setUp(self):
        """راه‌اندازی تست‌ها"""
        self.client = Client()
        
        # ایجاد کاربران
        self.normal_user = User.objects.create_user(
            username='normal_user',
            email='user@example.com',
            password='testpass123'
        )
        
        self.staff_user = User.objects.create_user(
            username='staff_user',
            email='staff@example.com',
            password='testpass123',
            is_staff=True
        )
        
        self.superuser = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='testpass123'
        )
    
    def test_admin_page_without_login(self):
        """تست: کاربر بدون لاگین نمی‌تواند به admin دسترسی داشته باشد"""
        response = self.client.get('/admin/')
        # باید ریدایرکت شود یا 302 بازگردد
        self.assertIn(response.status_code, [302, 401, 403])
    
    def test_dashboard_without_login(self):
        """تست: کاربر بدون لاگین نمی‌تواند به dashboard دسترسی داشته باشد"""
        response = self.client.get('/dashboard/')
        # باید ریدایرکت شود
        self.assertIn(response.status_code, [302, 401, 403])
    
    def test_admin_with_normal_user(self):
        """تست: کاربر عادی نمی‌تواند به admin دسترسی داشته باشد"""
        self.client.login(username='normal_user', password='testpass123')
        response = self.client.get('/admin/')
        # باید ریدایرکت شود یا خطا دهد
        self.assertIn(response.status_code, [302, 403])
    
    def test_dashboard_with_normal_user(self):
        """تست: کاربر عادی نمی‌تواند به dashboard دسترسی داشته باشد"""
        self.client.login(username='normal_user', password='testpass123')
        response = self.client.get('/dashboard/')
        # باید ریدایرکت شود
        self.assertIn(response.status_code, [302, 403])
    
    def test_admin_with_staff_user(self):
        """تست: کاربر staff می‌تواند به admin دسترسی داشته باشد"""
        self.client.login(username='staff_user', password='testpass123')
        response = self.client.get('/admin/')
        # باید 200 برگردد
        self.assertEqual(response.status_code, 200)
    
    def test_dashboard_with_staff_user(self):
        """تست: کاربر staff می‌تواند به dashboard دسترسی داشته باشد"""
        self.client.login(username='staff_user', password='testpass123')
        response = self.client.get('/dashboard/')
        # باید 200 برگردد
        self.assertEqual(response.status_code, 200)
    
    def test_blog_create_without_login(self):
        """تست: کاربر بدون لاگین نمی‌تواند پست ایجاد کند"""
        response = self.client.get('/blog/create/')
        # باید ریدایرکت شود
        self.assertIn(response.status_code, [302, 401, 403])
    
    def test_blog_create_with_normal_user(self):
        """تست: کاربر عادی نمی‌تواند پست ایجاد کند"""
        self.client.login(username='normal_user', password='testpass123')
        response = self.client.get('/blog/create/')
        # باید ریدایرکت شود
        self.assertIn(response.status_code, [302, 403])
    
    def test_blog_create_with_staff_user(self):
        """تست: کاربر staff می‌تواند پست ایجاد کند"""
        self.client.login(username='staff_user', password='testpass123')
        response = self.client.get('/blog/create/')
        # باید 200 برگردد
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    import unittest
    unittest.main()
