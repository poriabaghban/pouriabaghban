"""
Security Middleware برای محافظت از صفحات ادمین و داشبورد
"""

from django.shortcuts import redirect
from django.contrib import messages
from django.urls import resolve
from django.contrib.auth.decorators import user_passes_test
from django.core.cache import cache


class AdminSecurityMiddleware:
    """
    Middleware برای محافظت از صفحات ادمین و داشبورد
    اگر کاربر لاگین نکرده و سعی کند URL داشبورد یا ادمین را دسترسی دارد، ریدایرکت شود
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # صفحات محافظ‌شده
        self.protected_paths = [
            '/admin/',
            '/dashboard/',
        ]
    
    def __call__(self, request):
        # بررسی صفحات محافظ‌شده (بجز صفحات لاگین)
        for path in self.protected_paths:
            if request.path.startswith(path) and not request.path.startswith('/admin/login'):
                # اگر کاربر لاگین نکرده است
                if not request.user.is_authenticated:
                    messages.warning(request, '⚠️ لطفاً ابتدا وارد حساب خود شوید.')
                    return redirect('admin:login')
                
                # اگر صفحه admin است و کاربر staff نیست
                if path == '/admin/' and not request.user.is_staff:
                    messages.error(request, '❌ فقط مدیران می‌توانند این صفحه را ببینند.')
                    return redirect('home')
                
                # اگر صفحه dashboard است و کاربر staff نیست
                if path == '/dashboard/' and not request.user.is_staff:
                    messages.error(request, '❌ فقط مدیران می‌توانند این صفحه را ببینند.')
                    return redirect('home')
                
                if request.user.is_staff:
                  try:
                                cache.set(f"admin_presence_{request.user.id}", True, 90)
                  except Exception as e:
                                             print(f"Admin presence cache failed: {e}")

                break
        
        response = self.get_response(request)
        return response
