from django.db import models
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType


class UserRole(models.Model):
    """نقش‌های کاربری سفارشی"""
    ROLE_CHOICES = [
        ('admin', '🔑 ادمین - دسترسی کامل'),
        ('author', '✍️ نویسنده - می‌تواند پست بنویسد'),
        ('editor', '📝 ویرایشگر - می‌تواند پست‌های دیگران را ویرایش کند'),
        ('moderator', '🛡️ مدیریت‌کننده - می‌تواند کامنت‌ها را تایید کند'),
        ('subscriber', '👤 مشترک - فقط می‌تواند بخواند'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_role', verbose_name="کاربر")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, verbose_name="نقش")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    can_write = models.BooleanField(default=False, verbose_name="می‌تواند بنویسد")
    can_edit = models.BooleanField(default=False, verbose_name="می‌تواند ویرایش کند")
    can_delete = models.BooleanField(default=False, verbose_name="می‌تواند حذف کند")
    can_manage_comments = models.BooleanField(default=False, verbose_name="می‌تواند کامنت‌ها را مدیریت کند")
    can_manage_users = models.BooleanField(default=False, verbose_name="می‌تواند کاربران را مدیریت کند")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ به‌روزرسانی")
    
    class Meta:
        verbose_name = "نقش کاربر"
        verbose_name_plural = "نقش‌های کاربری"
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"
    
    def save(self, *args, **kwargs):
        """تنظیم خودکار اختیارات بر اساس نقش"""
        if self.role == 'admin':
            self.can_write = True
            self.can_edit = True
            self.can_delete = True
            self.can_manage_comments = True
            self.can_manage_users = True
            self.user.is_staff = True
            self.user.is_superuser = True
        elif self.role == 'author':
            self.can_write = True
            self.can_edit = True
            self.can_delete = False
            self.can_manage_comments = False
            self.can_manage_users = False
            self.user.is_staff = True
        elif self.role == 'editor':
            self.can_write = True
            self.can_edit = True
            self.can_delete = False
            self.can_manage_comments = False
            self.can_manage_users = False
            self.user.is_staff = True
        elif self.role == 'moderator':
            self.can_write = False
            self.can_edit = False
            self.can_delete = False
            self.can_manage_comments = True
            self.can_manage_users = False
            self.user.is_staff = True
        else:  # subscriber
            self.can_write = False
            self.can_edit = False
            self.can_delete = False
            self.can_manage_comments = False
            self.can_manage_users = False
            self.user.is_staff = False
        
        self.user.save()
        super().save(*args, **kwargs)
