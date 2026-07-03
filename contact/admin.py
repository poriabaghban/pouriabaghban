from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html

from .models import ContactMessage, ContactSetting


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("get_name_badge", "email", "subject", "created_at", "get_read_status", "get_reply_status")
    list_filter = ("is_read", "is_replied", "created_at")
    search_fields = ("name", "email", "subject", "message")
    readonly_fields = ("created_at", "replied_at", "get_full_message")
    actions = ["mark_as_read", "mark_as_unread", "mark_as_replied"]
    fieldsets = (
        ("اطلاعات فرستنده", {"fields": ("name", "email", "phone")}),
        ("پیام دریافت‌شده", {"fields": ("subject", "get_full_message", "created_at")}),
        ("وضعیت", {"fields": ("is_read", "is_replied")}),
        ("پاسخ شما", {"fields": ("reply_message", "replied_at")}),
    )

    def get_name_badge(self, obj):
        color = "#28a745" if obj.is_replied else "#ffc107"
        return format_html(
            '<span style="background-color: {}; padding: 5px 10px; border-radius: 3px; color: white;">{}</span>',
            color,
            obj.name,
        )
    get_name_badge.short_description = "نام"

    def get_read_status(self, obj):
        if obj.is_read:
            return format_html('<span style="color: green;">خوانده شده</span>')
        return format_html('<span style="color: red;">خوانده نشده</span>')
    get_read_status.short_description = "وضعیت خواندن"

    def get_reply_status(self, obj):
        if obj.is_replied:
            return format_html('<span style="color: green;">پاسخ داده شده</span>')
        return format_html('<span style="color: orange;">در انتظار پاسخ</span>')
    get_reply_status.short_description = "وضعیت پاسخ"

    def get_full_message(self, obj):
        return format_html('<div style="white-space: pre-wrap; background: #f5f5f5; padding: 10px; border-radius: 5px;">{}</div>', obj.message)
    get_full_message.short_description = "متن کامل پیام"

    def mark_as_read(self, request, queryset):
        count = queryset.update(is_read=True)
        self.message_user(request, f"{count} پیام به عنوان خوانده شده علامت‌گذاری شد.")
    mark_as_read.short_description = "علامت‌گذاری به عنوان خوانده شده"

    def mark_as_unread(self, request, queryset):
        count = queryset.update(is_read=False)
        self.message_user(request, f"{count} پیام به عنوان خوانده نشده علامت‌گذاری شد.")
    mark_as_unread.short_description = "علامت‌گذاری به عنوان خوانده نشده"

    def mark_as_replied(self, request, queryset):
        count = queryset.update(is_replied=True, is_read=True, replied_at=timezone.now())
        self.message_user(request, f"{count} پیام به عنوان پاسخ داده شده علامت‌گذاری شد.")
    mark_as_replied.short_description = "علامت‌گذاری به عنوان پاسخ داده شده"


@admin.register(ContactSetting)
class ContactSettingAdmin(admin.ModelAdmin):
    list_display = ("email", "phone")
    fieldsets = (
        ("اطلاعات تماس", {"fields": ("email", "phone", "address")}),
        ("شبکه‌های اجتماعی", {"fields": ("whatsapp", "telegram", "instagram", "linkedin")}),
    )

    def has_add_permission(self, request):
        return not ContactSetting.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
