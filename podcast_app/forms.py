import os

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError

from .models import Podcast, calculate_audio_file_hash


class PodcastAdminForm(forms.ModelForm):
    class Meta:
        model = Podcast
        fields = "__all__"

    def clean_audio_file(self):
        audio_file = self.cleaned_data.get("audio_file")
        if not audio_file:
            return audio_file

        max_size = getattr(settings, "MAX_AUDIO_FILE_SIZE", 30 * 1024 * 1024)
        allowed_extensions = getattr(
            settings,
            "ALLOWED_AUDIO_EXTENSIONS",
            [".mp3", ".wav", ".ogg", ".m4a", ".flac", ".aac"],
        )
        allowed_content_types = getattr(
            settings,
            "ALLOWED_AUDIO_CONTENT_TYPES",
            [
                "audio/mpeg",
                "audio/mp3",
                "audio/wav",
                "audio/x-wav",
                "audio/ogg",
                "audio/mp4",
                "audio/x-m4a",
                "audio/flac",
                "audio/aac",
            ],
        )

        if audio_file.size > max_size:
            raise ValidationError(
                f"\u062d\u062c\u0645 \u0641\u0627\u06cc\u0644 \u0635\u0648\u062a\u06cc \u0646\u0628\u0627\u06cc\u062f \u0628\u06cc\u0634\u062a\u0631 \u0627\u0632 {max_size // (1024 * 1024)} \u0645\u06af\u0627\u0628\u0627\u06cc\u062a \u0628\u0627\u0634\u062f."
            )

        ext = os.path.splitext(audio_file.name)[1].lower()
        if ext not in allowed_extensions:
            raise ValidationError(
                f"\u0641\u0642\u0637 \u0641\u0627\u06cc\u0644 \u0635\u0648\u062a\u06cc \u0645\u062c\u0627\u0632 \u0627\u0633\u062a. \u0641\u0631\u0645\u062a\u200c\u0647\u0627\u06cc \u0642\u0627\u0628\u0644 \u0642\u0628\u0648\u0644: {', '.join(allowed_extensions)}"
            )

        content_type = getattr(audio_file, "content_type", "")
        if content_type and content_type not in allowed_content_types:
            raise ValidationError(f"\u0646\u0648\u0639 \u0641\u0627\u06cc\u0644 \u0645\u0639\u062a\u0628\u0631 \u0646\u06cc\u0633\u062a: {content_type}")

        file_hash = calculate_audio_file_hash(audio_file)
        if file_hash:
            duplicates = Podcast.objects.filter(audio_file_sha256=file_hash)
            if self.instance and self.instance.pk:
                duplicates = duplicates.exclude(pk=self.instance.pk)
            if duplicates.exists():
                raise ValidationError("\u0627\u06cc\u0646 \u0641\u0627\u06cc\u0644 \u0635\u0648\u062a\u06cc \u0642\u0628\u0644\u0627 \u0628\u0631\u0627\u06cc \u06cc\u06a9 \u0634\u0639\u0631/\u067e\u0627\u062f\u06a9\u0633\u062a \u062b\u0628\u062a \u0634\u062f\u0647 \u0627\u0633\u062a.")
            self.instance.audio_file_sha256 = file_hash

        return audio_file

