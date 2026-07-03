import os
from uuid import uuid4

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from downloads.validators import validate_clean_text, validate_text_fields


User = get_user_model()


def chat_attachment_upload_to(instance, filename):
    now = timezone.localtime()
    return "chat_uploads/{0}/{1}/{2}/{3}_{4}".format(
        now.strftime("%Y"),
        now.strftime("%m"),
        now.strftime("%d"),
        uuid4().hex,
        os.path.basename(filename),
    )


def get_allowed_chat_attachment_extensions():
    return getattr(
        settings,
        "CHAT_ALLOWED_ATTACHMENT_EXTENSIONS",
        [
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".webp",
            ".avif",
            ".apng",
            ".bmp",
            ".heic",
            ".heif",
            ".ico",
            ".jfif",
            ".svg",
            ".tif",
            ".tiff",
            ".pdf",
            ".mp4",
            ".mov",
            ".avi",
            ".mkv",
            ".zip",
            ".doc",
            ".docx",
            ".xls",
            ".xlsx",
            ".ppt",
            ".pptx",
            ".txt",
        ],
    )


def validate_chat_attachment_extension(file_obj):
    ext = os.path.splitext(file_obj.name)[1].lower()
    if ext not in get_allowed_chat_attachment_extensions():
        raise ValidationError("فرمت فایل برای چت مجاز نیست.")


class ChatRoom(models.Model):
    GROUP = "group"
    PRIVATE = "private"

    ROOM_TYPE_CHOICES = (
        (GROUP, "گروهی"),
        (PRIVATE, "خصوصی"),
    )

    name = models.CharField(max_length=150, validators=[validate_clean_text], verbose_name="نام اتاق")
    room_type = models.CharField(
        max_length=20,
        choices=ROOM_TYPE_CHOICES,
        default=GROUP,
        verbose_name="نوع اتاق",
    )
    participants = models.ManyToManyField(
        User,
        blank=True,
        related_name="chat_rooms",
        verbose_name="اعضا",
        limit_choices_to={"is_staff": True},
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")

    class Meta:
        verbose_name = "اتاق چت"
        verbose_name_plural = "اتاق‌های چت"
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["room_type", "-created_at"]),
        ]

    def __str__(self):
        return self.name

    def clean(self):
        validate_text_fields(self, ("name",))

    def user_can_access(self, user):
        if not user or not user.is_authenticated or not user.is_staff:
            return False
        if self.room_type == self.GROUP:
            return True
        return self.participants.filter(pk=user.pk).exists()


class ChatMessage(models.Model):
    room = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name="messages",
        verbose_name="اتاق",
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_chat_messages",
        verbose_name="فرستنده",
    )
    text = models.TextField(blank=True, validators=[validate_clean_text], verbose_name="متن پیام")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="زمان ارسال")
    is_read = models.BooleanField(default=False, verbose_name="خوانده شده")
    read_by = models.ManyToManyField(
        User,
        blank=True,
        related_name="read_chat_messages",
        verbose_name="خوانده شده توسط",
    )

    class Meta:
        verbose_name = "پیام چت"
        verbose_name_plural = "پیام‌های چت"
        ordering = ("timestamp",)
        indexes = [
            models.Index(fields=["room", "-timestamp"]),
            models.Index(fields=["room", "-id"]),
            models.Index(fields=["sender", "-timestamp"]),
        ]

    def __str__(self):
        return f"{self.sender} - {self.room} - {self.timestamp:%Y-%m-%d %H:%M}"

    def clean(self):
        validate_text_fields(self, ("text",))


class MessageAttachment(models.Model):
    message = models.ForeignKey(
        ChatMessage,
        on_delete=models.CASCADE,
        related_name="attachments",
        verbose_name="پیام",
    )
    file = models.FileField(
        upload_to=chat_attachment_upload_to,
        validators=[validate_chat_attachment_extension],
        verbose_name="فایل",
    )
    original_filename = models.CharField(max_length=255, verbose_name="نام اصلی فایل")
    content_type = models.CharField(max_length=150, blank=True, verbose_name="نوع محتوا")
    size = models.PositiveBigIntegerField(default=0, verbose_name="حجم")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="زمان آپلود")

    class Meta:
        verbose_name = "ضمیمه پیام"
        verbose_name_plural = "ضمیمه‌های پیام"
        ordering = ("uploaded_at",)
        indexes = [
            models.Index(fields=["message", "uploaded_at"]),
        ]

    def __str__(self):
        return self.original_filename

    @property
    def filename(self):
        return os.path.basename(self.original_filename or self.file.name)
