import json
import time

from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.cache import cache

from .models import ChatMessage, ChatRoom
from downloads.validators import FORBIDDEN_TEXT_MESSAGE, validate_clean_text


MESSAGE_THROTTLE_LIMIT = 20
MESSAGE_THROTTLE_WINDOW = 60
RECENT_MESSAGES_CACHE_KEY = "admin_chat:room:{room_id}:recent_messages:v2"


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope.get("user")
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"admin_chat_{self.room_id}"
        self.online_key = f"admin_chat:room:{self.room_id}:online"
        self.throttle_key = f"admin_chat:user:{getattr(self.user, 'pk', 'anonymous')}:messages"

        if not self.user or not self.user.is_authenticated or not self.user.is_staff:
            await self.close(code=4403)
            return

        await self.accept()
        self.ready = False

        if not await self.can_access_room():
            await self.close(code=4403)
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        self.ready = True
        online_count = await self.add_online_user()
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "online_count",
                "online_count": online_count,
            },
        )

    async def disconnect(self, close_code):
        if hasattr(self, "room_group_name"):
            online_count = await self.remove_online_user()
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "online_count",
                    "online_count": online_count,
                },
            )

    async def receive(self, text_data=None, bytes_data=None):
        if not text_data:
            return

        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            await self.send_error("درخواست نامعتبر است.")
            return

        event_type = data.get("type")
        if not getattr(self, "ready", False):
            await self.send_error("Chat room is still loading. Please try again.")
            return

        if event_type == "message":
            await self.handle_message(data)
        elif event_type == "typing":
            await self.handle_typing(data)
        elif event_type == "read":
            await self.handle_read(data)
        else:
            await self.send_error("نوع رویداد پشتیبانی نمی‌شود.")

    async def handle_message(self, data):
        if not await self.allow_message():
            await self.send_error("تعداد پیام‌ها زیاد است. کمی بعد دوباره تلاش کنید.")
            return

        text = (data.get("text") or "").strip()
        client_message_id = data.get("client_message_id") or ""
        try:
            validate_clean_text(text)
        except Exception:
            await self.send_error(FORBIDDEN_TEXT_MESSAGE)
            return
        if len(text) > 5000:
            await self.send_error("متن پیام بیش از حد طولانی است.")
            return

        message = await self.create_message(text)
        payload = await self.serialize_message(message)
        await self.invalidate_recent_messages_cache()

        try:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message": payload,
                },
            )
        except Exception:
            await self.send_error("قطع اتصال")
            return

        await self.send(
            text_data=json.dumps(
                {
                    "type": "message_ack",
                    "client_message_id": client_message_id,
                    "message": payload,
                }
            )
        )

    async def handle_typing(self, data):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "typing_status",
                "user_id": self.user.pk,
                "username": self.user.get_username(),
                "is_typing": bool(data.get("is_typing")),
            },
        )

    async def handle_read(self, data):
        message_id = data.get("message_id")
        if not message_id:
            return
        updated = await self.mark_message_read(message_id)
        if updated:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "message_read",
                    "message_id": int(message_id),
                    "user_id": self.user.pk,
                    "username": self.user.get_username(),
                },
            )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({"type": "message", "message": event["message"]}))

    async def attachment_added(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "attachment_added",
                    "message_id": event["message_id"],
                    "attachment": event["attachment"],
                }
            )
        )

    async def typing_status(self, event):
        if event["user_id"] == self.user.pk:
            return
        await self.send(text_data=json.dumps({"type": "typing", **event}))

    async def message_read(self, event):
        await self.send(text_data=json.dumps({"type": "read", **event}))

    async def online_count(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "online_count",
                    "online_count": event["online_count"],
                }
            )
        )

    async def send_error(self, message):
        await self.send(text_data=json.dumps({"type": "error", "message": message}))

    @database_sync_to_async
    def can_access_room(self):
        try:
            room = ChatRoom.objects.only("id", "room_type").get(pk=self.room_id)
        except ChatRoom.DoesNotExist:
            return False
        if room.room_type == ChatRoom.GROUP:
            return True
        return room.participants.filter(pk=self.user.pk).exists()

    @database_sync_to_async
    def create_message(self, text):
        return ChatMessage.objects.create(room_id=self.room_id, sender=self.user, text=text)

    @database_sync_to_async
    def serialize_message(self, message):
        return {
            "id": message.pk,
            "room_id": message.room_id,
            "sender_id": message.sender_id,
            "sender_username": message.sender.get_username(),
            "sender": message.sender_id,
            "text": message.text,
            "timestamp": message.timestamp.isoformat(),
            "created_at": message.timestamp.isoformat(),
            "is_read": message.is_read,
            "attachments": [],
        }

    @database_sync_to_async
    def mark_message_read(self, message_id):
        try:
            message = ChatMessage.objects.select_related("room").get(pk=message_id, room_id=self.room_id)
        except ChatMessage.DoesNotExist:
            return False
        if message.sender_id == self.user.pk:
            return False
        message.read_by.add(self.user)
        if not message.is_read:
            message.is_read = True
            message.save(update_fields=["is_read"])
        return True

    @sync_to_async
    def add_online_user(self):
        users = set(cache.get(self.online_key, []))
        users.add(self.user.pk)
        cache.set(self.online_key, list(users), 120)
        return len(users)

    @sync_to_async
    def remove_online_user(self):
        users = set(cache.get(self.online_key, []))
        users.discard(self.user.pk)
        cache.set(self.online_key, list(users), 120)
        return len(users)

    @sync_to_async
    def allow_message(self):
        now = int(time.time())
        timestamps = [ts for ts in cache.get(self.throttle_key, []) if now - ts < MESSAGE_THROTTLE_WINDOW]
        if len(timestamps) >= MESSAGE_THROTTLE_LIMIT:
            cache.set(self.throttle_key, timestamps, MESSAGE_THROTTLE_WINDOW)
            return False
        timestamps.append(now)
        cache.set(self.throttle_key, timestamps, MESSAGE_THROTTLE_WINDOW)
        return True

    @sync_to_async
    def invalidate_recent_messages_cache(self):
        cache.delete(RECENT_MESSAGES_CACHE_KEY.format(room_id=self.room_id))
