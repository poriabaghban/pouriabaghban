from django.contrib import admin, messages
from django.db.models import Count

from .forms import (
    AllowedFileTypeAdminForm,
    DownloadCategoryAdminForm,
    DownloadItemAdminForm,
    DownloadPageSettingAdminForm,
)
from .models import (
    AllowedFileType,
    DownloadCategory,
    DownloadComment,
    DownloadItem,
    DownloadLog,
    DownloadPageSetting,
    DownloadReaction,
)


@admin.register(DownloadCategory)
class DownloadCategoryAdmin(admin.ModelAdmin):
    form = DownloadCategoryAdminForm
    list_display = ("name", "slug", "is_active", "created_at", "updated_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("name", "slug", "description")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(AllowedFileType)
class AllowedFileTypeAdmin(admin.ModelAdmin):
    form = AllowedFileTypeAdminForm
    list_display = ("name", "extension", "mime_type", "max_size_mb", "is_active", "updated_at")
    list_filter = ("is_active", "extension")
    search_fields = ("name", "extension", "mime_type")


@admin.register(DownloadItem)
class DownloadItemAdmin(admin.ModelAdmin):
    form = DownloadItemAdminForm
    list_display = (
        "title",
        "platform",
        "version",
        "category",
        "file_extension",
        "file_size_display",
        "is_latest",
        "is_active",
        "requires_login",
        "download_count",
        "updated_at",
    )
    list_filter = ("platform", "category", "is_latest", "is_active", "requires_login", "created_at")
    search_fields = ("title", "slug", "version", "description", "changelog", "installation_guide")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("allowed_users", "allowed_groups")
    readonly_fields = ("file_size", "file_extension", "download_count", "created_at", "updated_at")
    fieldsets = (
        (None, {"fields": ("title", "slug", "category", "platform", "version", "file")}),
        ("Content", {"fields": ("description", "changelog", "installation_guide")}),
        ("Access", {"fields": ("requires_login", "allowed_users", "allowed_groups")}),
        ("State", {"fields": ("is_latest", "is_active", "download_count", "file_size", "file_extension", "created_at", "updated_at")}),
    )

    def has_add_permission(self, request):
        return request.user.is_staff

    def has_change_permission(self, request, obj=None):
        return request.user.is_staff


@admin.action(description="Approve selected comments")
def approve_comments(modeladmin, request, queryset):
    updated = queryset.update(is_approved=True)
    messages.success(request, f"{updated} comments approved.")


@admin.action(description="Deactivate selected comments")
def deactivate_comments(modeladmin, request, queryset):
    updated = queryset.update(is_active=False)
    messages.success(request, f"{updated} comments deactivated.")


@admin.register(DownloadComment)
class DownloadCommentAdmin(admin.ModelAdmin):
    list_display = ("download_item", "name", "user", "is_approved", "is_active", "ip_address", "created_at")
    list_filter = ("is_approved", "is_active", "created_at", "download_item")
    search_fields = ("name", "comment", "user__username", "download_item__title")
    readonly_fields = ("download_item", "user", "name", "comment", "ip_address", "user_agent", "created_at", "updated_at")
    actions = (approve_comments, deactivate_comments)


@admin.register(DownloadReaction)
class DownloadReactionAdmin(admin.ModelAdmin):
    list_display = ("download_item", "reaction_type", "user", "session_key", "ip_address", "created_at")
    list_filter = ("reaction_type", "created_at")
    search_fields = ("download_item__title", "user__username", "session_key", "ip_address")
    readonly_fields = ("download_item", "user", "session_key", "reaction_type", "ip_address", "user_agent", "created_at", "updated_at")


@admin.register(DownloadLog)
class DownloadLogAdmin(admin.ModelAdmin):
    list_display = ("download_item", "user", "ip_address", "downloaded_at")
    list_filter = ("downloaded_at", "download_item")
    search_fields = ("download_item__title", "user__username", "ip_address", "user_agent")
    readonly_fields = ("user", "download_item", "ip_address", "user_agent", "downloaded_at")


@admin.register(DownloadPageSetting)
class DownloadPageSettingAdmin(admin.ModelAdmin):
    form = DownloadPageSettingAdminForm
    list_display = ("id", "comments_enabled", "reactions_enabled", "comment_moderation_enabled", "updated_at")
    readonly_fields = ("created_at", "updated_at")

    def has_add_permission(self, request):
        return not DownloadPageSetting.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
