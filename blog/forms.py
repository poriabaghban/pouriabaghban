from pathlib import Path
from urllib.parse import urlparse

from django import forms
from django.forms import inlineformset_factory
from django.utils.translation import gettext_lazy as _

from .sanitizers import sanitize_blog_html
from .models import BlogPost, BlogPostDetailImage, BlogTag


ALLOWED_AUDIO_EXTENSIONS = {".mp3", ".wav", ".ogg"}
ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".webm", ".ogg"}
ALLOWED_MEDIA_URL_SCHEMES = {"http", "https"}

try:
    from ckeditor.widgets import CKEditorWidget

    RICH_TEXT_WIDGET = CKEditorWidget
except Exception:
    RICH_TEXT_WIDGET = forms.Textarea


class BlogPostForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=BlogTag.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label=_("برچسب‌ها"),
    )

    class Meta:
        model = BlogPost
        fields = [
            "title_fa",
            "content_fa",
            "excerpt_fa",
            "title_en",
            "content_en",
            "excerpt_en",
            "title_de",
            "content_de",
            "excerpt_de",
            "title",
            "slug",
            "content",
            "excerpt",
            "author",
            "category",
            "tags",
            "image",
            "audio_file",
            "audio_url",
            "video_file",
            "video_url",
            "status",
            "is_active",
            "is_featured",
            "is_on_homepage",
        ]
        widgets = {
            "title_fa": forms.TextInput(attrs={"class": "form-control"}),
            "title_en": forms.TextInput(attrs={"class": "form-control"}),
            "title_de": forms.TextInput(attrs={"class": "form-control"}),
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "slug": forms.TextInput(attrs={"class": "form-control"}),
            "content_fa": RICH_TEXT_WIDGET(attrs={"class": "form-control", "rows": 10}),
            "content_en": RICH_TEXT_WIDGET(attrs={"class": "form-control", "rows": 10}),
            "content_de": RICH_TEXT_WIDGET(attrs={"class": "form-control", "rows": 10}),
            "content": RICH_TEXT_WIDGET(attrs={"class": "form-control", "rows": 10}),
            "excerpt_fa": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "excerpt_en": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "excerpt_de": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "excerpt": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "category": forms.Select(attrs={"class": "form-control"}),
            "image": forms.FileInput(attrs={"class": "form-control", "accept": "image/*"}),
            "audio_file": forms.FileInput(attrs={"class": "form-control", "accept": "audio/mpeg,audio/wav,audio/ogg,audio/mp3"}),
            "audio_url": forms.URLInput(attrs={"class": "form-control", "placeholder": _("https://example.com/audio.mp3")}),
            "video_file": forms.FileInput(attrs={"class": "form-control", "accept": "video/mp4,video/webm,video/ogg"}),
            "video_url": forms.URLInput(attrs={"class": "form-control", "placeholder": _("https://example.com/video.mp4")}),
            "status": forms.Select(attrs={"class": "form-control"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "is_featured": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "is_on_homepage": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
        labels = {
            "title_fa": _("عنوان فارسی"),
            "content_fa": _("محتوای فارسی"),
            "excerpt_fa": _("خلاصه فارسی"),
            "title_en": _("عنوان انگلیسی"),
            "content_en": _("محتوای انگلیسی"),
            "excerpt_en": _("خلاصه انگلیسی"),
            "title_de": _("عنوان آلمانی"),
            "content_de": _("محتوای آلمانی"),
            "excerpt_de": _("خلاصه آلمانی"),
            "title": _("عنوان قدیمی"),
            "slug": _("نشانی"),
            "content": _("محتوای قدیمی"),
            "excerpt": _("خلاصه قدیمی"),
            "category": _("دسته‌بندی"),
            "tags": _("برچسب‌ها"),
            "image": _("تصویر"),
            "audio_file": _("Audio file"),
            "audio_url": _("Audio URL"),
            "video_file": _("Video file"),
            "video_url": _("Video URL"),
            "is_active": _("Active"),
            "status": _("وضعیت"),
            "is_featured": _("برجسته"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "author" in self.fields:
            self.fields["author"].required = False
        if "status" in self.fields:
            self.fields["status"].choices = [
                ("draft", _("Draft")),
                ("published", _("Published")),
                ("archived", _("Archived")),
            ]

    def _clean_media_file(self, field_name, allowed_extensions, media_label):
        media_file = self.cleaned_data.get(field_name)
        if not media_file:
            return media_file
        extension = Path(media_file.name).suffix.lower()
        if extension not in allowed_extensions:
            raise forms.ValidationError(
                _("%(label)s must be one of these formats: %(formats)s."),
                params={"label": media_label, "formats": ", ".join(sorted(allowed_extensions))},
            )
        return media_file

    def _clean_media_url(self, field_name, allowed_extensions, media_label):
        media_url = (self.cleaned_data.get(field_name) or "").strip()
        if not media_url:
            return media_url
        parsed = urlparse(media_url)
        if parsed.scheme not in ALLOWED_MEDIA_URL_SCHEMES or not parsed.netloc:
            raise forms.ValidationError(_("Please enter a valid http or https URL."))
        extension = Path(parsed.path).suffix.lower()
        if not extension or extension not in allowed_extensions:
            raise forms.ValidationError(
                _("%(label)s URL must point to one of these formats: %(formats)s."),
                params={"label": media_label, "formats": ", ".join(sorted(allowed_extensions))},
            )
        return media_url

    def clean_audio_file(self):
        return self._clean_media_file("audio_file", ALLOWED_AUDIO_EXTENSIONS, _("Audio"))

    def clean_video_file(self):
        return self._clean_media_file("video_file", ALLOWED_VIDEO_EXTENSIONS, _("Video"))

    def clean_audio_url(self):
        return self._clean_media_url("audio_url", ALLOWED_AUDIO_EXTENSIONS, _("Audio"))

    def clean_video_url(self):
        return self._clean_media_url("video_url", ALLOWED_VIDEO_EXTENSIONS, _("Video"))

    def clean(self):
        cleaned_data = super().clean()
        for field in ("content_fa", "content_en", "content_de", "content"):
            cleaned_data[field] = sanitize_blog_html(cleaned_data.get(field))

        fa_complete = all((cleaned_data.get(field) or "").strip() for field in ("title_fa", "content_fa", "excerpt_fa"))
        en_complete = all((cleaned_data.get(field) or "").strip() for field in ("title_en", "content_en", "excerpt_en"))
        de_complete = all((cleaned_data.get(field) or "").strip() for field in ("title_de", "content_de", "excerpt_de"))
        legacy_complete = all((cleaned_data.get(field) or "").strip() for field in ("title", "content", "excerpt"))
        if not (fa_complete or en_complete or de_complete or legacy_complete):
            raise forms.ValidationError(_("لطفا حداقل یک زبان را کامل وارد کنید."))
        return cleaned_data


class BlogPostDetailImageForm(forms.ModelForm):
    class Meta:
        model = BlogPostDetailImage
        fields = ["image", "title", "content", "order"]
        widgets = {
            "image": forms.FileInput(attrs={"class": "form-control", "accept": "image/*"}),
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "content": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "order": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
        }
        labels = {
            "image": _("عکس جزئیات"),
            "title": _("تیتر عکس"),
            "content": _("متن کنار یا زیر عکس"),
            "order": _("ترتیب"),
        }


BlogPostDetailImageFormSet = inlineformset_factory(
    BlogPost,
    BlogPostDetailImage,
    form=BlogPostDetailImageForm,
    extra=4,
    can_delete=True,
)
