import os
from uuid import uuid4

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

from .validators import validate_clean_text, validate_kskh_file


User = get_user_model()


def kskh_upload_to(instance, filename):
    now = timezone.localtime()
    ext = os.path.splitext(filename)[1].lower()
    return f"kskh/{now:%Y}/{now:%m}/{uuid4().hex}{ext}"


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


class KskhPost(TimeStampedModel):
    APP = "app"
    CONFIG = "config"
    OTHER = "other"
    KIND_CHOICES = (
        (APP, "App"),
        (CONFIG, "Config"),
        (OTHER, "Other"),
    )

    title = models.CharField(max_length=180, validators=[validate_clean_text])
    slug = models.SlugField(max_length=210, unique=True, blank=True)
    description = models.TextField(blank=True, validators=[validate_clean_text])
    file = models.FileField(upload_to=kskh_upload_to, validators=[validate_kskh_file])
    file_size = models.PositiveBigIntegerField(default=0, editable=False)
    file_extension = models.CharField(max_length=20, blank=True, editable=False)
    kind = models.CharField(max_length=20, choices=KIND_CHOICES, default=OTHER)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="kskh_uploads")
    is_active = models.BooleanField(default=True)
    download_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "KSKH post"
        verbose_name_plural = "KSKH posts"

    def __str__(self):
        return self.title

    def clean(self):
        validate_clean_text(self.title)
        validate_clean_text(self.description)
        if self.file:
            validate_kskh_file(self.file)

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title, allow_unicode=True) or uuid4().hex[:10]
            slug = base
            counter = 2
            while KskhPost.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{counter}"
                counter += 1
            self.slug = slug
        if self.file:
            self.file_size = self.file.size
            self.file_extension = os.path.splitext(self.file.name)[1].lower()
            if self.file_extension in {".apk", ".apks", ".aab", ".xapk", ".ipa", ".exe"}:
                self.kind = self.APP
            elif self.file_extension in {".conf", ".config", ".json", ".yaml", ".yml", ".txt", ".ovpn"}:
                self.kind = self.CONFIG
        super().save(*args, **kwargs)

    @property
    def file_size_display(self):
        return file_size_label(self.file_size)

    @property
    def file_name(self):
        return os.path.basename(self.file.name) if self.file else ""

    def get_absolute_url(self):
        return reverse("kskh:detail", kwargs={"slug": self.slug})


class KskhComment(TimeStampedModel):
    post = models.ForeignKey(KskhPost, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="kskh_comments")
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="replies")
    body = models.TextField(validators=[validate_clean_text])
    is_approved = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("created_at",)
        verbose_name = "KSKH comment"
        verbose_name_plural = "KSKH comments"

    def __str__(self):
        return f"{self.user} - {self.post}"

    def clean(self):
        validate_clean_text(self.body)

    @property
    def can_show(self):
        return self.is_active and self.is_approved


class KskhReaction(TimeStampedModel):
    LIKE = "like"
    DISLIKE = "dislike"
    REACTION_CHOICES = (
        (LIKE, "Like"),
        (DISLIKE, "Dislike"),
    )

    post = models.ForeignKey(KskhPost, on_delete=models.CASCADE, related_name="reactions")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="kskh_reactions")
    session_key = models.CharField(max_length=40, blank=True)
    reaction_type = models.CharField(max_length=20, choices=REACTION_CHOICES)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    class Meta:
        ordering = ("-created_at",)
        constraints = [
            models.UniqueConstraint(fields=("post", "user"), condition=models.Q(user__isnull=False), name="unique_kskh_user_reaction"),
            models.UniqueConstraint(fields=("post", "session_key"), condition=models.Q(user__isnull=True), name="unique_kskh_session_reaction"),
        ]

    def __str__(self):
        return f"{self.post} - {self.reaction_type}"
