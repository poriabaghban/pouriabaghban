from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group


class Message(models.Model):
    content = models.TextField(verbose_name='متن')

    def __str__(self):
        return self.content[:50]


class GroupMessage(models.Model):
    MESSAGE_TYPE_TEXT = 'text'
    MESSAGE_TYPE_STICKER = 'sticker'
    MESSAGE_TYPE_FILE = 'file'

    MESSAGE_TYPE_CHOICES = (
        (MESSAGE_TYPE_TEXT, 'متن'),
        (MESSAGE_TYPE_STICKER, 'استیکر'),
        (MESSAGE_TYPE_FILE, 'فایل'),
    )

    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='messages', verbose_name='گروه')
    user = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True, verbose_name='کاربر')
    recipients = models.ManyToManyField(
        get_user_model(),
        blank=True,
        related_name='received_group_messages',
        verbose_name='گیرندگان',
    )
    read_by = models.ManyToManyField(
        get_user_model(),
        blank=True,
        related_name='read_group_messages',
        verbose_name='خوانده شده توسط',
    )
    reply_to = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='replies',
        verbose_name='در پاسخ به',
    )
    content = models.TextField(blank=True, verbose_name='متن')
    attachment = models.FileField(upload_to='chat_attachments/%Y/%m/', blank=True, null=True, verbose_name='پیوست')
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPE_CHOICES, default=MESSAGE_TYPE_TEXT, verbose_name='نوع پیام')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='زمان ارسال')
    is_deleted = models.BooleanField(default=False, verbose_name='حذف شده')
    deleted_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deleted_group_messages',
        verbose_name='حذف شده توسط',
    )
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name='زمان حذف')

    class Meta:
        ordering = ('created_at',)
        verbose_name = 'پیام گروهی'
        verbose_name_plural = 'پیام‌های گروهی'

    def __str__(self):
        user = self.user.get_full_name() if self.user else 'anonymous'
        preview = self.content or (self.attachment.name if self.attachment else '')
        return f"{user}: {preview[:40]}"
