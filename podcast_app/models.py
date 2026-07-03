import hashlib
import os

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.storage import FileSystemStorage
from django.db import models


secure_podcast_storage = FileSystemStorage(
    location=settings.BASE_DIR / "protected_media" / "podcasts",
    base_url=None,
)


def get_allowed_audio_extensions():
    return getattr(
        settings,
        "ALLOWED_AUDIO_EXTENSIONS",
        [".mp3", ".wav", ".ogg", ".m4a", ".flac", ".aac"],
    )


def get_max_audio_file_size():
    return getattr(settings, "MAX_AUDIO_FILE_SIZE", 30 * 1024 * 1024)


def validate_audio_file_extension(value):
    ext = os.path.splitext(value.name)[1].lower()
    allowed = get_allowed_audio_extensions()
    if ext not in allowed:
        raise ValidationError(
            "\u0641\u0642\u0637 \u0641\u0627\u06cc\u0644 \u0635\u0648\u062a\u06cc \u0645\u062c\u0627\u0632 \u0627\u0633\u062a. \u0641\u0631\u0645\u062a\u200c\u0647\u0627\u06cc \u0642\u0627\u0628\u0644 \u0642\u0628\u0648\u0644: %(formats)s",
            params={"formats": ", ".join(allowed)},
        )


def validate_audio_file_size(value):
    max_size = get_max_audio_file_size()
    if value.size > max_size:
        raise ValidationError(
            "\u062d\u062c\u0645 \u0641\u0627\u06cc\u0644 \u0635\u0648\u062a\u06cc \u0646\u0628\u0627\u06cc\u062f \u0628\u06cc\u0634\u062a\u0631 \u0627\u0632 %(size)s \u0645\u06af\u0627\u0628\u0627\u06cc\u062a \u0628\u0627\u0634\u062f.",
            params={"size": max_size // (1024 * 1024)},
        )


def calculate_audio_file_hash(file_obj):
    if not file_obj:
        return ""

    original_position = None
    try:
        original_position = file_obj.tell()
    except Exception:
        pass

    should_close = False
    try:
        if hasattr(file_obj, "open") and not getattr(file_obj, "file", None):
            file_obj.open("rb")
            should_close = True

        digest = hashlib.sha256()
        if hasattr(file_obj, "chunks"):
            for chunk in file_obj.chunks():
                digest.update(chunk)
        else:
            for chunk in iter(lambda: file_obj.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()
    finally:
        try:
            if original_position is not None:
                file_obj.seek(original_position)
            else:
                file_obj.seek(0)
        except Exception:
            pass
        if should_close:
            try:
                file_obj.close()
            except Exception:
                pass


class Podcast(models.Model):
    CONTENT_REGULAR = "regular"
    CONTENT_SPECIAL = "special"
    CONTENT_TYPE_CHOICES = (
        (CONTENT_REGULAR, "\u067e\u0627\u062f\u06a9\u0633\u062a"),
        (CONTENT_SPECIAL, "\u0634\u0639\u0631 \u0648\u06cc\u0698\u0647"),
    )

    content_type = models.CharField(
        max_length=20,
        choices=CONTENT_TYPE_CHOICES,
        default=CONTENT_REGULAR,
        db_index=True,
        verbose_name="\u0646\u0648\u0639 \u0645\u062d\u062a\u0648\u0627",
    )
    title = models.CharField(max_length=200, verbose_name="\u0639\u0646\u0648\u0627\u0646")
    speaker = models.CharField(max_length=100, verbose_name="\u06af\u0648\u06cc\u0646\u062f\u0647 / \u0646\u0648\u06cc\u0633\u0646\u062f\u0647")
    description = models.TextField(verbose_name="\u062a\u0648\u0636\u06cc\u062d\u0627\u062a \u06a9\u0648\u062a\u0627\u0647")
    transcript = models.TextField(blank=True, verbose_name="\u0645\u062a\u0646 \u067e\u0627\u062f\u06a9\u0633\u062a")
    audio_file = models.FileField(
        storage=secure_podcast_storage,
        upload_to="",
        blank=True,
        null=True,
        validators=[validate_audio_file_extension, validate_audio_file_size],
        verbose_name="\u0641\u0627\u06cc\u0644 \u0635\u0648\u062a\u06cc",
        help_text="\u0641\u0642\u0637 \u0641\u0627\u06cc\u0644 \u0635\u0648\u062a\u06cc \u0628\u0627 \u062d\u062c\u0645 \u062d\u062f\u0627\u06a9\u062b\u0631 \u06f3\u06f0 \u0645\u06af\u0627\u0628\u0627\u06cc\u062a \u067e\u0630\u06cc\u0631\u0641\u062a\u0647 \u0645\u06cc\u200c\u0634\u0648\u062f.",
    )
    cover_image = models.ImageField(
        upload_to="podcast_covers/",
        blank=True,
        null=True,
        verbose_name="\u0639\u06a9\u0633",
    )
    audio_file_sha256 = models.CharField(
        max_length=64,
        blank=True,
        db_index=True,
        editable=False,
        verbose_name="\u0627\u062b\u0631 \u0627\u0646\u06af\u0634\u062a \u0641\u0627\u06cc\u0644 \u0635\u0648\u062a\u06cc",
    )
    duration = models.CharField(max_length=20, blank=True, verbose_name="\u0645\u062f\u062a \u0632\u0645\u0627\u0646")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="\u062a\u0627\u0631\u06cc\u062e \u0627\u0646\u062a\u0634\u0627\u0631")
    is_published = models.BooleanField(default=True, verbose_name="\u0645\u0646\u062a\u0634\u0631 \u0634\u062f\u0647")
    category = models.CharField(max_length=50, blank=True, verbose_name="\u062f\u0633\u062a\u0647\u200c\u0628\u0646\u062f\u06cc")
    views = models.PositiveIntegerField(
        default=0,
        editable=False,
        verbose_name="\u062a\u0639\u062f\u0627\u062f \u0628\u0627\u0632\u062f\u06cc\u062f",
    )

    class Meta:
        verbose_name = "\u067e\u0627\u062f\u06a9\u0633\u062a"
        verbose_name_plural = "\u067e\u0627\u062f\u06a9\u0633\u062a\u200c\u0647\u0627"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def clean(self):
        super().clean()
        if self.audio_file:
            file_hash = self.audio_file_sha256 or calculate_audio_file_hash(self.audio_file)
            if file_hash:
                duplicates = Podcast.objects.filter(audio_file_sha256=file_hash)
                if self.pk:
                    duplicates = duplicates.exclude(pk=self.pk)
                if duplicates.exists():
                    raise ValidationError({
                        "audio_file": "\u0627\u06cc\u0646 \u0641\u0627\u06cc\u0644 \u0635\u0648\u062a\u06cc \u0642\u0628\u0644\u0627 \u0628\u0631\u0627\u06cc \u06cc\u06a9 \u0634\u0639\u0631/\u067e\u0627\u062f\u06a9\u0633\u062a \u062b\u0628\u062a \u0634\u062f\u0647 \u0627\u0633\u062a."
                    })

    def save(self, *args, **kwargs):
        if self.audio_file:
            self.audio_file_sha256 = calculate_audio_file_hash(self.audio_file)
            duplicates = Podcast.objects.filter(audio_file_sha256=self.audio_file_sha256)
            if self.pk:
                duplicates = duplicates.exclude(pk=self.pk)
            if duplicates.exists():
                raise ValidationError({
                    "audio_file": "\u0627\u06cc\u0646 \u0641\u0627\u06cc\u0644 \u0635\u0648\u062a\u06cc \u0642\u0628\u0644\u0627 \u0628\u0631\u0627\u06cc \u06cc\u06a9 \u0634\u0639\u0631/\u067e\u0627\u062f\u06a9\u0633\u062a \u062b\u0628\u062a \u0634\u062f\u0647 \u0627\u0633\u062a."
                })
        else:
            self.audio_file_sha256 = ""
        super().save(*args, **kwargs)

    @property
    def total_views(self):
        return self.views or 0

    def get_file_size(self):
        if not self.audio_file:
            return "-"
        try:
            size = self.audio_file.size
        except Exception:
            return "\u0646\u0627\u0645\u0634\u062e\u0635"
        if size < 1024:
            return f"{size} B"
        if size < 1024 * 1024:
            return f"{size / 1024:.2f} KB"
        return f"{size / (1024 * 1024):.2f} MB"

    def get_file_extension(self):
        if not self.audio_file:
            return ""
        return os.path.splitext(self.audio_file.name)[1].lower()

    def get_jalali_date(self):
        try:
            import jdatetime

            local_date = self.created_at.astimezone()
            return jdatetime.datetime.fromgregorian(datetime=local_date).strftime("%Y/%m/%d")
        except Exception:
            return self.created_at.strftime("%Y/%m/%d") if self.created_at else "-"


class SpecialPoem(Podcast):
    class Meta:
        proxy = True
        verbose_name = "\u0634\u0639\u0631 \u0648\u06cc\u0698\u0647"
        verbose_name_plural = "\u0634\u0639\u0631 \u0648\u06cc\u0698\u0647"

