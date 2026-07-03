import json
from json import JSONDecodeError

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group as AuthGroup
from django.db import models
from django.utils import timezone

from .models import GroupMessage


class GroupChatConsumer(AsyncWebsocketConsumer):
    online_channels = {}

    async def connect(self):
        self.group_id = self.scope['url_route']['kwargs']['group_id']
        self.room_group_name = f'admin_group_{self.group_id}'

        user = self.scope.get('user')
        if not user or not user.is_authenticated or not user.is_staff:
            await self.close()
            return

        if not await self.group_exists(self.group_id):
            await self.close()
            return

        self.user_id = user.id
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        self._add_online_channel(self.room_group_name, self.user_id, self.channel_name)
        await self.broadcast_presence()

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            self._remove_online_channel(self.room_group_name, getattr(self, 'user_id', None), self.channel_name)
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
            await self.broadcast_presence()

    async def receive(self, text_data=None, bytes_data=None):
        if text_data is None:
            return

        try:
            data = json.loads(text_data)
        except JSONDecodeError:
            return

        if data.get('type') == 'read':
            await self.send_read_receipt(data)
            return
        if data.get('type') == 'typing':
            await self.channel_layer.group_send(self.room_group_name, {
                'type': 'typing_status',
                'user_id': self.user_id,
                'username': self.scope['user'].get_full_name() or self.scope['user'].username,
                'is_typing': bool(data.get('is_typing')),
            })
            return

        message_type = data.get('type') or GroupMessage.MESSAGE_TYPE_TEXT
        if message_type not in {GroupMessage.MESSAGE_TYPE_TEXT, GroupMessage.MESSAGE_TYPE_STICKER, GroupMessage.MESSAGE_TYPE_FILE}:
            message_type = GroupMessage.MESSAGE_TYPE_TEXT

        message = (data.get('message') or '').strip()
        if not message:
            return

        user = self.scope.get('user')
        username = 'کاربر'
        if user and user.is_authenticated:
            username = user.get_full_name() or user.username

        recipient_ids = [int(value) for value in data.get('recipients', []) if str(value).isdigit()]
        reply_to_id = data.get('reply_to')
        saved_message = await self.save_message(self.group_id, user, message, message_type, recipient_ids, reply_to_id)
        if saved_message is None:
            return

        await self.channel_layer.group_send(self.room_group_name, {
            'type': 'chat_message',
            'id': saved_message['id'],
            'message': message,
            'message_type': message_type,
            'username': username,
            'sender_id': user.id if user and user.is_authenticated else None,
            'recipient_ids': saved_message['recipient_ids'],
            'read_by_ids': [],
            'read_by_names': [],
            'created_at': saved_message['created_at'],
            'reply_to': saved_message['reply_to'],
            'is_deleted': False,
        })

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'event': 'message',
            'id': event.get('id'),
            'message': event['message'],
            'type': event.get('message_type', GroupMessage.MESSAGE_TYPE_TEXT),
            'username': event.get('username'),
            'sender_id': event.get('sender_id'),
            'recipient_ids': event.get('recipient_ids', []),
            'read_by_ids': event.get('read_by_ids', []),
            'read_by_names': event.get('read_by_names', []),
            'created_at': event.get('created_at'),
            'attachment_url': event.get('attachment_url', ''),
            'attachment_name': event.get('attachment_name', ''),
            'reply_to': event.get('reply_to'),
            'is_deleted': event.get('is_deleted', False),
        }))

    async def read_receipt(self, event):
        await self.send(text_data=json.dumps({
            'event': 'read_receipt',
            'message_ids': event.get('message_ids', []),
            'reader_id': event.get('reader_id'),
            'reader_name': event.get('reader_name'),
        }))

    async def presence(self, event):
        await self.send(text_data=json.dumps({
            'event': 'presence',
            'online_user_ids': event.get('online_user_ids', []),
        }))

    async def typing_status(self, event):
        if event.get('user_id') == self.user_id:
            return
        await self.send(text_data=json.dumps({
            'event': 'typing',
            'user_id': event.get('user_id'),
            'username': event.get('username'),
            'is_typing': event.get('is_typing', False),
        }))

    async def message_deleted(self, event):
        await self.send(text_data=json.dumps({
            'event': 'message_deleted',
            'message_id': event.get('message_id'),
            'deleted_by_id': event.get('deleted_by_id'),
            'deleted_by_name': event.get('deleted_by_name'),
        }))

    async def send_read_receipt(self, data):
        ids = [int(value) for value in data.get('ids', []) if str(value).isdigit()]
        if not ids:
            return
        user = self.scope.get('user')
        read_ids = await self.mark_messages_read(self.group_id, user, ids)
        if read_ids:
            await self.channel_layer.group_send(self.room_group_name, {
                'type': 'read_receipt',
                'message_ids': read_ids,
                'reader_id': user.id,
                'reader_name': user.get_full_name() or user.username,
            })

    async def broadcast_presence(self):
        await self.channel_layer.group_send(self.room_group_name, {
            'type': 'presence',
            'online_user_ids': self._online_user_ids(self.room_group_name),
        })

    @classmethod
    def _add_online_channel(cls, room, user_id, channel_name):
        cls.online_channels.setdefault(room, {}).setdefault(user_id, set()).add(channel_name)

    @classmethod
    def _remove_online_channel(cls, room, user_id, channel_name):
        if user_id is None:
            return
        user_channels = cls.online_channels.get(room, {}).get(user_id)
        if not user_channels:
            return
        user_channels.discard(channel_name)
        if not user_channels:
            cls.online_channels.get(room, {}).pop(user_id, None)

    @classmethod
    def _online_user_ids(cls, room):
        return sorted(cls.online_channels.get(room, {}).keys())

    @database_sync_to_async
    def group_exists(self, group_id):
        return AuthGroup.objects.filter(pk=group_id).exists()

    @database_sync_to_async
    def save_message(self, group_id, user, message, message_type, recipient_ids, reply_to_id=None):
        try:
            group = AuthGroup.objects.get(pk=group_id)
        except AuthGroup.DoesNotExist:
            return None

        member_ids = set(group.user_set.filter(is_staff=True, is_active=True).values_list('id', flat=True))
        if not member_ids:
            member_ids = set(get_user_model().objects.filter(is_staff=True, is_active=True).values_list('id', flat=True))
        clean_recipient_ids = sorted((set(recipient_ids) & member_ids) - {user.id})
        if not clean_recipient_ids:
            clean_recipient_ids = sorted(member_ids - {user.id})

        reply_to = None
        if reply_to_id and str(reply_to_id).isdigit():
            reply_to = GroupMessage.objects.select_related('user').filter(
                group=group,
                pk=int(reply_to_id),
                is_deleted=False,
            ).filter(
                models.Q(recipients__isnull=True) | models.Q(user=user) | models.Q(recipients=user)
            ).distinct().first()

        saved = GroupMessage.objects.create(
            group=group,
            user=user if user and user.is_authenticated else None,
            content=message,
            message_type=message_type,
            reply_to=reply_to,
        )
        saved.recipients.set(clean_recipient_ids)
        reply_payload = None
        if reply_to:
            reply_payload = {
                'id': reply_to.pk,
                'message': reply_to.content,
                'type': reply_to.message_type,
                'username': (reply_to.user.get_full_name() or reply_to.user.username) if reply_to.user else 'کاربر',
            }
        return {
            'id': saved.pk,
            'recipient_ids': clean_recipient_ids,
            'created_at': timezone.localtime(saved.created_at).strftime('%Y-%m-%d %H:%M'),
            'reply_to': reply_payload,
        }

    @database_sync_to_async
    def mark_messages_read(self, group_id, user, ids):
        if not user or not user.is_authenticated:
            return []
        messages = GroupMessage.objects.filter(
            group_id=group_id,
            pk__in=ids,
            is_deleted=False,
        ).exclude(user=user).filter(
            models.Q(recipients__isnull=True) | models.Q(recipients=user)
        ).distinct()
        read_ids = []
        for message in messages:
            message.read_by.add(user)
            read_ids.append(message.pk)
        return read_ids

