from django.contrib import admin
from django.utils.html import format_html

from .forms import ChatRoomAdminForm
from .models import ChatMessage, ChatRoom, MessageAttachment


class MessageAttachmentInline(admin.TabularInline):
    model = MessageAttachment
    extra = 0
    readonly_fields = ("original_filename", "content_type", "size", "uploaded_at", "file_link")
    fields = ("original_filename", "content_type", "size", "uploaded_at", "file_link")
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

    def file_link(self, obj):
        if obj and obj.file:
            return format_html('<a href="{}" target="_blank">دانلود</a>', obj.file.url)
        return "-"
    file_link.short_description = "فایل"


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    form = ChatRoomAdminForm
    list_display = ("name", "room_type", "created_at", "participants_count")
    list_filter = ("room_type", "created_at")
    search_fields = ("name", "participants__username", "participants__email")
    filter_horizontal = ("participants",)
    readonly_fields = ("created_at",)

    def participants_count(self, obj):
        return obj.participants.count()
    participants_count.short_description = "تعداد اعضا"


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ("room", "sender", "short_text", "timestamp", "is_read")
    list_filter = ("room", "is_read", "timestamp")
    search_fields = ("text", "sender__username", "room__name")
    readonly_fields = ("room", "sender", "text", "timestamp", "is_read", "read_by")
    inlines = (MessageAttachmentInline,)

    def short_text(self, obj):
        return obj.text[:80] if obj.text else "فایل ضمیمه"
    short_text.short_description = "متن"


@admin.register(MessageAttachment)
class MessageAttachmentAdmin(admin.ModelAdmin):
    list_display = ("original_filename", "message", "content_type", "size", "uploaded_at")
    list_filter = ("content_type", "uploaded_at")
    search_fields = ("original_filename", "message__text", "message__sender__username")
    readonly_fields = ("message", "file", "original_filename", "content_type", "size", "uploaded_at")


