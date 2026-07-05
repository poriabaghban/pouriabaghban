from django.contrib import admin, messages
from django.utils.html import format_html

from .models import KskhComment, KskhPost, KskhReaction


@admin.action(description="تایید فایل‌های انتخاب‌شده و نمایش در پنل کاربر")
def approve_posts(modeladmin, request, queryset):
    updated = queryset.update(is_active=True)
    messages.success(request, f"{updated} فایل تایید شد و در پنل کاربر نمایش داده می‌شود.")


@admin.action(description="غیرفعال کردن فایل‌های انتخاب‌شده")
def deactivate_posts(modeladmin, request, queryset):
    updated = queryset.update(is_active=False)
    messages.success(request, f"{updated} فایل غیرفعال شد و از پنل کاربر مخفی شد.")


@admin.action(description="Approve selected comments")
def approve_comments(modeladmin, request, queryset):
    updated = queryset.update(is_approved=True)
    messages.success(request, f"{updated} comments approved.")


@admin.action(description="Deactivate selected comments")
def deactivate_comments(modeladmin, request, queryset):
    updated = queryset.update(is_active=False)
    messages.success(request, f"{updated} comments deactivated.")


@admin.register(KskhPost)
class KskhPostAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "kind",
        "file_extension",
        "file_size_display",
        "approval_status",
        "download_count",
        "created_at",
    )

    list_filter = (
        "kind",
        "is_active",
        "created_at",
    )

    search_fields = (
        "title",
        "description",
        "slug",
    )

    prepopulated_fields = {
        "slug": ("title",)
    }

    readonly_fields = (
        "file_size",
        "file_extension",
        "download_count",
        "created_at",
        "updated_at",
    )

    actions = (
        approve_posts,
        deactivate_posts,
    )

    ordering = (
        "-created_at",
    )

    def approval_status(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="'
                'background:#16a34a;'
                'color:white;'
                'padding:5px 12px;'
                'border-radius:999px;'
                'font-weight:bold;'
                'font-size:12px;'
                'display:inline-block;'
                'min-width:95px;'
                'text-align:center;'
                '">تایید شده</span>'
            )

        return format_html(
            '<span style="'
            'background:#facc15;'
            'color:#3a2f00;'
            'padding:5px 12px;'
            'border-radius:999px;'
            'font-weight:bold;'
            'font-size:12px;'
            'display:inline-block;'
            'min-width:110px;'
            'text-align:center;'
            '">در انتظار تایید</span>'
        )

    approval_status.short_description = "وضعیت تایید"


@admin.register(KskhComment)
class KskhCommentAdmin(admin.ModelAdmin):
    list_display = (
        "post",
        "user",
        "parent",
        "is_approved",
        "is_active",
        "created_at",
    )

    list_filter = (
        "is_approved",
        "is_active",
        "created_at",
    )

    search_fields = (
        "body",
        "user__username",
        "post__title",
    )

    actions = (
        approve_comments,
        deactivate_comments,
    )


@admin.register(KskhReaction)
class KskhReactionAdmin(admin.ModelAdmin):
    list_display = (
        "post",
        "reaction_type",
        "user",
        "session_key",
        "ip_address",
        "created_at",
    )

    list_filter = (
        "reaction_type",
        "created_at",
    )

    search_fields = (
        "post__title",
        "user__username",
        "session_key",
        "ip_address",
    )

    readonly_fields = (
        "post",
        "user",
        "session_key",
        "reaction_type",
        "ip_address",
        "user_agent",
        "created_at",
        "updated_at",
    )