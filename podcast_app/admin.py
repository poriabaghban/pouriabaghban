import mimetypes
import os

from django.contrib import admin
from django.http import FileResponse, Http404
from django.urls import path, reverse
from django.utils.html import format_html

from .forms import PodcastAdminForm
from .models import Podcast, SpecialPoem


class BasePodcastAdmin(admin.ModelAdmin):
    form = PodcastAdminForm
    empty_value_display = "-"
    list_per_page = 25
    save_on_top = True
    list_display = (
        "title",
        "speaker",
        "audio_status",
        "get_file_size_display",
        "get_jalali_date_display",
        "total_views_display",
        "is_published",
        "duration",
    )
    base_content_type = None

    list_filter = (
        "is_published",
        "category",
        "created_at",
        ("audio_file", admin.EmptyFieldListFilter),
    )
    list_editable = ("is_published",)
    search_fields = ("title", "speaker", "description", "transcript")
    readonly_fields = (
        "created_at",
        "total_views_display",
        "get_jalali_date_display",
        "get_file_size_display",
        "audio_preview",
        "cover_preview",
    )
    ordering = ("-created_at",)
    fieldsets = (
        ("اطلاعات اصلی پادکست", {
            "fields": ("title", "speaker", "category", "duration", "is_published"),
        }),
        ("متن و توضیحات", {
            "fields": ("description", "transcript"),
        }),
        ("فایل صوتی", {
            "fields": ("audio_file", "audio_preview", "get_file_size_display"),
            "classes": ("wide",),
            "description": "فقط فایل صوتی با حجم حداکثر ۳۰ مگابایت پذیرفته می‌شود.",
        }),
        ("تصویر", {
            "fields": ("cover_image", "cover_preview"),
            "classes": ("wide",),
        }),
        ("آمار و تاریخ", {
            "fields": ("created_at", "total_views_display", "get_jalali_date_display"),
            "classes": ("collapse",),
        }),
    )
    actions = ["publish_podcasts", "unpublish_podcasts"]

    def get_urls(self):
        urls = super().get_urls()
        url_name = f"{self.model._meta.app_label}_{self.model._meta.model_name}_audio_preview"
        custom_urls = [
            path(
                "<int:podcast_id>/audio-preview/",
                self.admin_site.admin_view(self.audio_preview_view),
                name=url_name,
            ),
        ]
        return custom_urls + urls

    def audio_preview_view(self, request, podcast_id):
        podcast = self.get_queryset(request).filter(pk=podcast_id).first()
        if not podcast or not podcast.audio_file:
            raise Http404("Audio file not found.")

        try:
            file_path = podcast.audio_file.path
        except Exception as exc:
            raise Http404("Audio file is not available.") from exc

        if not os.path.exists(file_path):
            raise Http404("Audio file not found.")

        content_type = mimetypes.guess_type(file_path)[0] or "audio/mpeg"
        response = FileResponse(open(file_path, "rb"), content_type=content_type)
        response["Content-Disposition"] = 'inline; filename="podcast-audio"'
        response["X-Content-Type-Options"] = "nosniff"
        return response

    def audio_status(self, obj):
        if obj.audio_file:
            return format_html(
                '<span class="podcast-audio-ok" title="{}">دارای صوت</span>',
                obj.get_file_size(),
            )
        return format_html('<span class="podcast-audio-missing">بدون صوت</span>')
    audio_status.short_description = "وضعیت صوت"
    audio_status.admin_order_field = "audio_file"

    def audio_preview(self, obj):
        if not obj or not obj.pk:
            return "پس از ذخیره پادکست، پیش‌نمایش صوت نمایش داده می‌شود."
        if not obj.audio_file:
            return "فایل صوتی ثبت نشده است."
        ext = obj.get_file_extension() or os.path.splitext(obj.audio_file.name)[1]
        url_name = f"admin:{self.model._meta.app_label}_{self.model._meta.model_name}_audio_preview"
        audio_url = reverse(url_name, args=[obj.pk])
        content_type = mimetypes.types_map.get(ext, "audio/mpeg")
        player = format_html(
            '<audio controls controlsList="nodownload" preload="metadata"><source src="{}" type="{}"></audio>',
            audio_url,
            content_type,
        )
        return format_html(
            '''
            <div class="podcast-audio-preview">
                {}
                <div class="podcast-audio-meta">
                    <span>نام: {}</span>
                    <span>حجم: {}</span>
                    <span>فرمت: {}</span>
                    <span>وضعیت: فایل محافظت‌شده و قابل پخش برای مدیر</span>
                </div>
            </div>
            ''',
            player,
            os.path.basename(obj.audio_file.name),
            obj.get_file_size(),
            ext,
        )
    audio_preview.short_description = "پیش‌نمایش صوت"

    def cover_preview(self, obj):
        if obj and obj.cover_image:
            return format_html(
                '<img class="podcast-cover-preview" src="{}" alt="{}" />',
                obj.cover_image.url,
                obj.title,
            )
        return "عکسی انتخاب نشده است."
    cover_preview.short_description = "پیش‌نمایش عکس"

    def get_jalali_date_display(self, obj):
        if not obj or not obj.pk or not obj.created_at:
            return "پس از ذخیره ثبت می‌شود"
        return obj.get_jalali_date()
    get_jalali_date_display.short_description = "تاریخ انتشار"
    get_jalali_date_display.admin_order_field = "created_at"

    def get_file_size_display(self, obj):
        if not obj or not obj.audio_file:
            return "فایلی ثبت نشده"
        return obj.get_file_size()
    get_file_size_display.short_description = "حجم فایل صوتی"
    get_file_size_display.admin_order_field = "audio_file"

    def total_views_display(self, obj):
        return obj.total_views if obj and obj.pk else 0
    total_views_display.short_description = "تعداد بازدید"

    def publish_podcasts(self, request, queryset):
        count = queryset.update(is_published=True)
        self.message_user(request, f"{count} پادکست منتشر شد.")
    publish_podcasts.short_description = "انتشار پادکست‌های انتخابی"

    def unpublish_podcasts(self, request, queryset):
        count = queryset.update(is_published=False)
        self.message_user(request, f"{count} پادکست از انتشار خارج شد.")
    unpublish_podcasts.short_description = "خارج کردن پادکست‌های انتخابی از انتشار"

    class Media:
        css = {"all": ("admin/css/podcast_admin.css",)}
        js = ("admin/js/podcast_admin.js",)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if self.base_content_type:
            return queryset.filter(content_type=self.base_content_type)
        return queryset

    def save_model(self, request, obj, form, change):
        if self.base_content_type:
            obj.content_type = self.base_content_type
        super().save_model(request, obj, form, change)


@admin.register(Podcast)
class PodcastAdmin(BasePodcastAdmin):
    base_content_type = Podcast.CONTENT_REGULAR


@admin.register(SpecialPoem)
class SpecialPoemAdmin(BasePodcastAdmin):
    base_content_type = Podcast.CONTENT_SPECIAL


