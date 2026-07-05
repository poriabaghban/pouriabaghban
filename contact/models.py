from django.db import models


class ContactMessage(models.Model):
    first_name = models.CharField("نام", max_length=100)
    last_name = models.CharField("نام خانوادگی", max_length=100)
    email = models.EmailField("ایمیل")
    phone = models.CharField("شماره تلفن", max_length=11)
    message = models.TextField("پیام", blank=True, null=True)
    created_at = models.DateTimeField("تاریخ ثبت", auto_now_add=True)
    is_read = models.BooleanField("خوانده شده؟", default=False)

    class Meta:
        verbose_name = "پیام تماس"
        verbose_name_plural = "پیام‌های تماس"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.phone}"