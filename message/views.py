from asgiref.sync import async_to_sync
try:
    from channels.layers import get_channel_layer
except ImportError:
    get_channel_layer = None
from django.contrib.admin.views.decorators import staff_member_required
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST
from django.views.generic import ListView

from .models import GroupMessage, Message
from pages.views import get_page_sections, get_all_skills, get_site_settings


class message_view(ListView):
    model = Message
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sections'] = get_page_sections('index')
        context['skills'] = get_all_skills()
        context['site_settings'] = get_site_settings()
        context['title'] = 'صفحه اصلی'
        return context


def _group_staff_users(group):
    User = get_user_model()
    members = group.user_set.filter(is_staff=True, is_active=True).order_by('first_name', 'last_name', 'username')
    if members.exists():
        return members
    return User.objects.filter(is_staff=True, is_active=True).order_by('first_name', 'last_name', 'username')


def _online_member_ids(members):
    return [member.id for member in members if cache.get(f'admin_presence_{member.id}')]


def _visible_messages(group, user):
    return GroupMessage.objects.select_related('user', 'group', 'reply_to', 'reply_to__user').prefetch_related('read_by', 'recipients').filter(
        Q(group=group),
        Q(recipients__isnull=True) | Q(user=user) | Q(recipients=user),
    ).distinct()


def _display_name(user):
    if not user:
        return 'کاربر'
    return user.get_full_name() or user.username


def _reply_payload(message):
    if not message or message.is_deleted:
        return None
    return {
        'id': message.pk,
        'message': message.content,
        'type': message.message_type,
        'username': _display_name(message.user),
    }


def _message_payload(saved, user, recipient_ids):
    attachment_url = saved.attachment.url if saved.attachment else ''
    attachment_name = saved.attachment.name.rsplit('/', 1)[-1] if saved.attachment else ''
    read_users = list(saved.read_by.all())
    return {
        'id': saved.pk,
        'message': saved.content,
        'message_type': saved.message_type,
        'type': saved.message_type,
        'username': _display_name(user),
        'sender_id': user.id,
        'recipient_ids': recipient_ids,
        'read_by_ids': [reader.id for reader in read_users],
        'read_by_names': [_display_name(reader) for reader in read_users],
        'created_at': timezone.localtime(saved.created_at).strftime('%Y-%m-%d %H:%M'),
        'attachment_url': attachment_url,
        'attachment_name': attachment_name,
        'reply_to': _reply_payload(saved.reply_to),
        'is_deleted': saved.is_deleted,
    }


@staff_member_required
@require_POST
def send_group_message(request, group_id):
    group = get_object_or_404(Group, pk=group_id)
    message_type = request.POST.get('type') or GroupMessage.MESSAGE_TYPE_TEXT
    if message_type not in {GroupMessage.MESSAGE_TYPE_TEXT, GroupMessage.MESSAGE_TYPE_STICKER, GroupMessage.MESSAGE_TYPE_FILE}:
        message_type = GroupMessage.MESSAGE_TYPE_TEXT

    content = (request.POST.get('message') or '').strip()
    attachment = request.FILES.get('attachment')
    if attachment:
        message_type = GroupMessage.MESSAGE_TYPE_FILE

    if not content and not attachment:
        return JsonResponse({'ok': False, 'error': 'empty_message'}, status=400)

    member_ids = set(_group_staff_users(group).values_list('id', flat=True))
    requested_recipient_ids = {
        int(value) for value in request.POST.getlist('recipients') if str(value).isdigit()
    }
    recipient_ids = sorted((requested_recipient_ids & member_ids) - {request.user.id})
    if not recipient_ids:
        recipient_ids = sorted(member_ids - {request.user.id})

    reply_to = None
    reply_to_id = request.POST.get('reply_to')
    if reply_to_id and str(reply_to_id).isdigit():
        reply_to = _visible_messages(group, request.user).filter(pk=int(reply_to_id), is_deleted=False).first()

    saved = GroupMessage.objects.create(
        group=group,
        user=request.user,
        content=content,
        message_type=message_type,
        attachment=attachment,
        reply_to=reply_to,
    )
    saved.recipients.set(recipient_ids)
    saved = GroupMessage.objects.select_related('user', 'reply_to', 'reply_to__user').prefetch_related('read_by').get(pk=saved.pk)

    payload = _message_payload(saved, request.user, recipient_ids)

    channel_layer = get_channel_layer() if get_channel_layer is not None else None
    if channel_layer is None:
        return JsonResponse({'ok': False, 'error': 'connection_lost'}, status=503)

    try:
        async_to_sync(channel_layer.group_send)(
            f'admin_group_{group.pk}',
            {
                'type': 'chat_message',
                **payload,
            },
        )
    except Exception:
        return JsonResponse({'ok': False, 'error': 'connection_lost'}, status=503)

    return JsonResponse({
        'ok': True,
        'id': payload['id'],
        'message': payload['message'],
        'type': payload['message_type'],
        'username': payload['username'],
        'sender_id': payload['sender_id'],
        'recipient_ids': payload['recipient_ids'],
        'read_by_ids': payload['read_by_ids'],
        'read_by_names': payload['read_by_names'],
        'created_at': payload['created_at'],
        'attachment_url': payload['attachment_url'],
        'attachment_name': payload['attachment_name'],
        'reply_to': payload['reply_to'],
        'is_deleted': payload['is_deleted'],
    })


@staff_member_required
@require_POST
def mark_group_messages_read(request, group_id):
    group = get_object_or_404(Group, pk=group_id)
    ids = [int(value) for value in request.POST.getlist('ids') if str(value).isdigit()]
    if not ids:
        return JsonResponse({'ok': True, 'read_ids': []})

    messages = _visible_messages(group, request.user).filter(pk__in=ids).exclude(user=request.user)
    read_ids = []
    for message in messages:
        message.read_by.add(request.user)
        read_ids.append(message.pk)

    if read_ids:
        channel_layer = get_channel_layer() if get_channel_layer is not None else None
        if channel_layer is not None:
            async_to_sync(channel_layer.group_send)(
                f'admin_group_{group.pk}',
                {
                    'type': 'read_receipt',
                    'message_ids': read_ids,
                    'reader_id': request.user.id,
                    'reader_name': request.user.get_full_name() or request.user.username,
                },
            )

    return JsonResponse({'ok': True, 'read_ids': read_ids})


@staff_member_required
@require_POST
def delete_group_message(request, group_id, message_id):
    group = get_object_or_404(Group, pk=group_id)
    message = get_object_or_404(_visible_messages(group, request.user), pk=message_id)
    if message.is_deleted:
        return JsonResponse({'ok': True, 'id': message.pk})

    message.is_deleted = True
    message.deleted_by = request.user
    message.deleted_at = timezone.now()
    message.content = ''
    message.attachment.delete(save=False)
    message.attachment = None
    message.save(update_fields=['is_deleted', 'deleted_by', 'deleted_at', 'content', 'attachment'])

    channel_layer = get_channel_layer() if get_channel_layer is not None else None
    if channel_layer is not None:
        async_to_sync(channel_layer.group_send)(
            f'admin_group_{group.pk}',
            {
                'type': 'message_deleted',
                'message_id': message.pk,
                'deleted_by_id': request.user.id,
                'deleted_by_name': _display_name(request.user),
            },
        )

    return JsonResponse({'ok': True, 'id': message.pk})


@staff_member_required
@require_GET
def group_members_presence(request, group_id):
    group = get_object_or_404(Group, pk=group_id)
    members = list(_group_staff_users(group))
    return JsonResponse({'ok': True, 'online_user_ids': _online_member_ids(members)})
