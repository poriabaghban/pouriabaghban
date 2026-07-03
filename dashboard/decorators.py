"""
Decorators برای محافظت از صفحات ادمین و داشبورد
جلوگیری از دسترسی غیرمجاز و هک وبسایت
"""

from functools import wraps
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.urls import reverse


def admin_required(view_func):
    """
    Decorator برای محافظت از صفحات ادمین و داشبورد
    فقط کاربران لاگین‌شده و staff می‌توانند وارد شوند
    """
    @wraps(view_func)
    @login_required(login_url='accounts:login')
    @user_passes_test(lambda u: u.is_staff, login_url='accounts:login')
    def wrapper(request, *args, **kwargs):
        # اگر کاربر staff نیست، به لاگین برو
        if not request.user.is_staff:
            messages.error(request, '❌ شما دسترسی ندارید. فقط کاربران مدیریت می‌توانند این صفحه را ببینند.')
            return redirect('accounts:login')
        return view_func(request, *args, **kwargs)
    return wrapper


def staff_only(view_func):
    """
    محافظ کننده سادی برای صفحات staff
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, '⚠️ لطفاً ابتدا وارد حساب خود شوید.')
            return redirect('accounts:login')
        
        if not request.user.is_staff:
            messages.error(request, '❌ شما دسترسی ندارید.')
            return redirect('home')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def superuser_only(view_func):
    """
    محافظ کننده برای صفحات تنها برای superuser
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, '⚠️ لطفاً ابتدا وارد حساب خود شوید.')
            return redirect('accounts:login')
        
        if not request.user.is_superuser:
            messages.error(request, '❌ فقط مدیران کل می‌توانند این صفحه را ببینند.')
            return redirect('home')
        
        return view_func(request, *args, **kwargs)
    return wrapper
