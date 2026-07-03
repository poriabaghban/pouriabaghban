from django.db import models
from django.utils import timezone

class ContactMessage(models.Model):
    name = models.CharField(max_length=100, verbose_name="نام")
    email = models.EmailField(verbose_name="ایمیل")
    phone = models.CharField(max_length=20, blank=True, verbose_name="شماره تماس")
    subject = models.CharField(max_length=200, verbose_name="موضوع")
    message = models.TextField(verbose_name="پیام")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    is_read = models.BooleanField(default=False, verbose_name="خوانده شده")
    is_replied = models.BooleanField(default=False, verbose_name="پاسخ داده شده")
    reply_message = models.TextField(blank=True, null=True, verbose_name="پیام پاسخ")
    replied_at = models.DateTimeField(blank=True, null=True, verbose_name="تاریخ پاسخ")
    
    class Meta:
        verbose_name = "پیام تماس"
        verbose_name_plural = "پیام های تماس"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"پیام از {self.name} - {self.subject}"
    
    def mark_as_read(self):
        self.is_read = True
        self.save()
    
    def reply(self, reply_message):
        self.reply_message = reply_message
        self.is_replied = True
        self.replied_at = timezone.now()
        self.save()


class ContactSetting(models.Model):
    email = models.EmailField(verbose_name="ایمیل پاسخ")
    phone = models.CharField(max_length=20, verbose_name="شماره تماس")
    address = models.TextField(verbose_name="آدرس")
    whatsapp = models.CharField(max_length=20, blank=True, verbose_name="واتساپ")
    telegram = models.CharField(max_length=50, blank=True, verbose_name="تلگرام")
    instagram = models.CharField(max_length=50, blank=True, verbose_name="اینستاگرام")
    linkedin = models.CharField(max_length=100, blank=True, verbose_name="لینکدین")
    
    class Meta:
        verbose_name = "تنظیمات تماس"
        verbose_name_plural = "تنظیمات تماس"
    
    def __str__(self):
        return "تنظیمات تماس"
