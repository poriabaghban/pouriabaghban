from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import GroupAdmin as DefaultGroupAdmin
from django.contrib.auth.models import Group
from django.core.cache import cache
from django.db.models import Q
from django.http import Http404
from django.shortcuts import render
from django.urls import path, reverse
from django.utils.html import format_html

from .models import GroupMessage, Message


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('short_content',)
    search_fields = ('content',)

    def short_content(self, obj):
        return obj.content[:80]

    short_content.short_description = 'متن'


@admin.register(GroupMessage)
class GroupMessageAdmin(admin.ModelAdmin):
    list_display = ('group', 'user', 'message_type', 'short_content', 'recipient_count', 'read_count', 'is_deleted', 'created_at')
    list_filter = ('message_type', 'is_deleted', 'group', 'created_at')
    search_fields = ('content', 'user__username', 'user__first_name', 'user__last_name', 'group__name')
    readonly_fields = ('created_at', 'deleted_at')
    filter_horizontal = ('recipients', 'read_by')

    def short_content(self, obj):
        return (obj.content or obj.attachment.name or '')[:80]

    def recipient_count(self, obj):
        return obj.recipients.count()

    def read_count(self, obj):
        return obj.read_by.count()

    short_content.short_description = 'پیام'
    recipient_count.short_description = 'گیرندگان'
    read_count.short_description = 'خوانده شده'


try:
    admin.site.unregister(Group)
except admin.sites.NotRegistered:
    pass


@admin.register(Group)
class GroupChatAdmin(DefaultGroupAdmin):
    change_form_template = 'admin/auth/group/change_form.html'
    list_display = ('name', 'chat_link')

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<path:object_id>/chat/', self.admin_site.admin_view(self.group_chat_view), name='auth_group_chat'),
        ]
        return custom_urls + urls

    def chat_link(self, obj):
        url = reverse('admin:auth_group_chat', args=[obj.pk])
        return format_html('<a class="button" href="{}">چت گروه</a>', url)

    chat_link.short_description = 'چت'

    def group_chat_view(self, request, object_id):
        try:
            group = Group.objects.get(pk=object_id)
        except Group.DoesNotExist as exc:
            raise Http404 from exc

        User = get_user_model()
        chat_members = group.user_set.filter(is_staff=True, is_active=True).order_by('first_name', 'last_name', 'username')
        if not chat_members.exists():
            chat_members = User.objects.filter(is_staff=True, is_active=True).order_by('first_name', 'last_name', 'username')
        chat_members = list(chat_members)

        recent_messages = GroupMessage.objects.select_related('user', 'group', 'reply_to', 'reply_to__user').prefetch_related('read_by', 'recipients').filter(
            Q(group=group),
            Q(recipients__isnull=True) | Q(user=request.user) | Q(recipients=request.user),
        ).distinct().order_by('-created_at')[:80]
        recent_messages = list(reversed(list(recent_messages)))
        for message in recent_messages:
            read_users = list(message.read_by.all())
            message.read_user_ids = [reader.id for reader in read_users]
            message.read_user_names = [reader.get_full_name() or reader.username for reader in read_users]
            message.recipient_user_ids = list(message.recipients.values_list('id', flat=True))
            message.attachment_url = message.attachment.url if message.attachment else ''
            message.attachment_name = message.attachment.name.rsplit('/', 1)[-1] if message.attachment else ''
            if message.reply_to and not message.reply_to.is_deleted:
                message.reply_to_payload = {
                    'id': message.reply_to_id,
                    'message': message.reply_to.content,
                    'type': message.reply_to.message_type,
                    'username': (message.reply_to.user.get_full_name() or message.reply_to.user.username) if message.reply_to.user else 'کاربر',
                }
            else:
                message.reply_to_payload = None

        online_user_ids = [member.id for member in chat_members if cache.get(f'admin_presence_{member.id}')]

        context = {
            **self.admin_site.each_context(request),
            'title': f'چت گروه {group.name}',
            'group': group,
            'recent_messages': recent_messages,
            'chat_members': chat_members,
            'online_user_ids': online_user_ids,
            'opts': self.model._meta,
        }
        return render(request, 'admin/group_chat.html', context)
