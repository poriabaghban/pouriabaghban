from django.contrib import admin, messages

from .models import KskhComment, KskhPost, KskhReaction


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
    list_display = ("title", "kind", "file_extension", "file_size_display", "is_active", "download_count", "created_at")
    list_filter = ("kind", "is_active", "created_at")
    search_fields = ("title", "description", "slug")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("file_size", "file_extension", "download_count", "created_at", "updated_at")


@admin.register(KskhComment)
class KskhCommentAdmin(admin.ModelAdmin):
    list_display = ("post", "user", "parent", "is_approved", "is_active", "created_at")
    list_filter = ("is_approved", "is_active", "created_at")
    search_fields = ("body", "user__username", "post__title")
    actions = (approve_comments, deactivate_comments)


@admin.register(KskhReaction)
class KskhReactionAdmin(admin.ModelAdmin):
    list_display = ("post", "reaction_type", "user", "session_key", "ip_address", "created_at")
    list_filter = ("reaction_type", "created_at")
    search_fields = ("post__title", "user__username", "session_key", "ip_address")
    readonly_fields = ("post", "user", "session_key", "reaction_type", "ip_address", "user_agent", "created_at", "updated_at")
