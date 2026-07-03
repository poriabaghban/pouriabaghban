import os
from uuid import uuid4

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.db import models
from django.core.files.storage import FileSystemStorage
from django.utils.text import slugify
from django.utils import timezone

from .validators import validate_clean_text, validate_text_fields


User = get_user_model()
protected_download_storage = FileSystemStorage(location=settings.PROTECTED_MEDIA_ROOT)


def download_upload_to(instance, filename):
    now = timezone.localtime()
    ext = os.path.splitext(filename)[1].lower()
    return "downloads/{0}/{1}/{2}{3}".format(
        now.strftime("%Y"),
        now.strftime("%m"),
        uuid4().hex,
        ext,
    )


def file_size_label(size):
    size = int(size or 0)
    if size < 1024:
        return f"{size} B"
    if size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    return f"{size / (1024 * 1024):.1f} MB"


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class DownloadCategory(TimeStampedModel):
    name = models.CharField(max_length=120, validators=[validate_clean_text])
    slug = models.SlugField(max_length=140, unique=True)
    description = models.TextField(blank=True, validators=[validate_clean_text])
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("name",)
        verbose_name = "Download category"
        verbose_name_plural = "Download categories"

    def __str__(self):
        return self.name

    def clean(self):
        validate_text_fields(self, ("name", "description"))

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)


class AllowedFileType(TimeStampedModel):
    name = models.CharField(max_length=80, validators=[validate_clean_text])
    extension = models.CharField(max_length=20, unique=True)
    mime_type = models.CharField(max_length=120, blank=True)
    max_size_mb = models.PositiveIntegerField(default=50)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("extension",)
        verbose_name = "Allowed file type"
        verbose_name_plural = "Allowed file types"

    def __str__(self):
        return f"{self.name} ({self.extension})"

    def clean(self):
        validate_text_fields(self, ("name", "mime_type"))
        extension = (self.extension or "").strip().lower()
        if not extension.startswith("."):
            extension = f".{extension}"
        if any(char in extension for char in ('<', '>', '}', '/', '"', "'")):
            raise ValidationError({"extension": "Extension contains a forbidden character."})
        self.extension = extension


class DownloadItem(TimeStampedModel):
    ANDROID = "android"
    WINDOWS = "windows"
    CONFIG = "config"
    OTHER = "other"
    PLATFORM_CHOICES = (
        (ANDROID, "Android"),
        (WINDOWS, "Windows"),
        (CONFIG, "Config"),
        (OTHER, "Other"),
    )

    title = models.CharField(max_length=180, validators=[validate_clean_text])
    slug = models.SlugField(max_length=200, unique=True)
    category = models.ForeignKey(DownloadCategory, on_delete=models.PROTECT, related_name="items")
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES, default=OTHER)
    version = models.CharField(max_length=50, blank=True, validators=[validate_clean_text])
    file = models.FileField(upload_to=download_upload_to, storage=protected_download_storage)
    file_size = models.PositiveBigIntegerField(default=0, editable=False)
    file_extension = models.CharField(max_length=20, blank=True, editable=False)
    description = models.TextField(blank=True, validators=[validate_clean_text])
    changelog = models.TextField(blank=True, validators=[validate_clean_text])
    installation_guide = models.TextField(blank=True, validators=[validate_clean_text])
    is_latest = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    requires_login = models.BooleanField(default=True)
    allowed_users = models.ManyToManyField(User, blank=True, related_name="allowed_downloads")
    allowed_groups = models.ManyToManyField(Group, blank=True, related_name="allowed_downloads")
    download_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("-is_latest", "-created_at")
        verbose_name = "Download item"
        verbose_name_plural = "Download items"

    def __str__(self):
        return self.title

    @property
    def file_size_display(self):
        return file_size_label(self.file_size)

    def clean(self):
        validate_text_fields(self, ("title", "version", "description", "changelog", "installation_guide"))
        if self.file:
            ext = os.path.splitext(self.file.name)[1].lower()
            allowed = AllowedFileType.objects.filter(extension=ext, is_active=True).first()
            if not allowed:
                raise ValidationError({"file": "This file extension is not allowed."})
            if self.file.size > allowed.max_size_mb * 1024 * 1024:
                raise ValidationError({"file": f"File is larger than {allowed.max_size_mb} MB."})
            mime_type = getattr(self.file, "content_type", "")
            if allowed.mime_type and mime_type and allowed.mime_type != mime_type:
                raise ValidationError({"file": "Uploaded file MIME type is not allowed."})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        if self.file:
            self.file_size = self.file.size
            self.file_extension = os.path.splitext(self.file.name)[1].lower()
        super().save(*args, **kwargs)

    def user_can_download(self, user):
        if user and user.is_authenticated and (user.is_staff or user.is_superuser):
            return True
        if self.requires_login and (not user or not user.is_authenticated):
            return False
        if not self.requires_login:
            return True
        allowed_user_ids = set(self.allowed_users.values_list("id", flat=True))
        allowed_group_ids = set(self.allowed_groups.values_list("id", flat=True))
        if not allowed_user_ids and not allowed_group_ids:
            return True
        if user.id in allowed_user_ids:
            return True
        return user.groups.filter(id__in=allowed_group_ids).exists()


class DownloadLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    download_item = models.ForeignKey(DownloadItem, on_delete=models.CASCADE, related_name="logs")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    downloaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-downloaded_at",)

    def __str__(self):
        return f"{self.download_item} - {self.user or 'anonymous'}"


class DownloadComment(TimeStampedModel):
    download_item = models.ForeignKey(DownloadItem, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=120, validators=[validate_clean_text])
    comment = models.TextField(validators=[validate_clean_text])
    is_approved = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.name} - {self.download_item}"

    def clean(self):
        validate_text_fields(self, ("name", "comment"))


class DownloadReaction(TimeStampedModel):
    LIKE = "like"
    BROKEN_HEART = "broken_heart"
    REACTION_CHOICES = (
        (LIKE, "Like"),
        (BROKEN_HEART, "Broken heart"),
    )

    download_item = models.ForeignKey(DownloadItem, on_delete=models.CASCADE, related_name="reactions")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, blank=True)
    reaction_type = models.CharField(max_length=20, choices=REACTION_CHOICES)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.download_item} - {self.reaction_type}"


class DownloadPageSetting(TimeStampedModel):
    comment_notice_text = models.TextField(
        default="For your security, you do not need to enter your email address. Only your name is required.",
        validators=[validate_clean_text],
    )
    comments_enabled = models.BooleanField(default=True)
    reactions_enabled = models.BooleanField(default=True)
    comment_moderation_enabled = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Download page setting"
        verbose_name_plural = "Download page settings"

    def __str__(self):
        return "Download page settings"

    def clean(self):
        validate_text_fields(self, ("comment_notice_text",))
        if not self.pk and DownloadPageSetting.objects.exists():
            raise ValidationError("Only one download page setting row is allowed.")

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_solo(cls):
        obj, _created = cls.objects.get_or_create(pk=1)
        return obj
