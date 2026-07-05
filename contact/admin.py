from django.contrib import admin
from django.utils.html import format_html
from .models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "phone",
        "email",
        "status_badge",
        "created_at",
    )

    list_filter = (
        "is_read",
        "created_at",
    )

    search_fields = (
        "first_name",
        "last_name",
        "phone",
        "email",
        "message",
    )

    readonly_fields = (
        "first_name",
        "last_name",
        "phone",
        "email",
        "message",
        "created_at",
        "status_badge",
    )

    ordering = ("-created_at",)

    actions = (
        "mark_as_read",
        "mark_as_unread",
    )

    fieldsets = (
        ("اطلاعات کاربر", {
            "fields": (
                "first_name",
                "last_name",
                "phone",
                "email",
            )
        }),
        ("پیام", {
            "fields": (
                "message",
            )
        }),
        ("وضعیت", {
            "fields": (
                "status_badge",
                "is_read",
                "created_at",
            )
        }),
    )

    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    full_name.short_description = "نام و نام خانوادگی"

    def status_badge(self, obj):
        if obj.is_read:
            return format_html(
                '<span style="'
                'background:#16a34a;'
                'color:white;'
                'padding:6px 12px;'
                'border-radius:999px;'
                'font-weight:bold;'
                'font-size:13px;'
                'display:inline-block;'
                'min-width:110px;'
                'text-align:center;'
                '">خوانده شده</span>'
            )

        return format_html(
            '<span style="'
            'background:#facc15;'
            'color:#3a2f00;'
            'padding:6px 12px;'
            'border-radius:999px;'
            'font-weight:bold;'
            'font-size:13px;'
            'display:inline-block;'
            'min-width:130px;'
            'text-align:center;'
            '">در انتظار خواندن</span>'
        )

    status_badge.short_description = "وضعیت"

    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f"{updated} پیام به حالت خوانده شده تغییر کرد.")

    mark_as_read.short_description = "علامت‌گذاری به عنوان خوانده شده"

    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False)
        self.message_user(request, f"{updated} پیام به حالت در انتظار خواندن تغییر کرد.")

    mark_as_unread.short_description = "علامت‌گذاری به عنوان در انتظار خواندن"