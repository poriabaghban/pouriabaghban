import os
import shutil
import mimetypes
from pathlib import Path
from uuid import uuid4

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.cache import cache
from django.db import transaction
from django.db.models import Q
from django.http import FileResponse, Http404, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from .forms import ChunkUploadForm
from .models import ChatMessage, ChatRoom, MessageAttachment
from downloads.validators import validate_clean_text

RECENT_MESSAGES_LIMIT = 50
RECENT_MESSAGES_CACHE_TIMEOUT = 30


def staff_required(view_func):
    return login_required(user_passes_test(lambda user: user.is_staff)(view_func))


def serialize_attachment(attachment):
    return {
        "id": attachment.pk,
        "url": reverse("admin_chat:attachment_file", kwargs={"pk": attachment.pk}),
        "filename": attachment.original_filename,
        "content_type": attachment.content_type,
        "size": attachment.size,
    }


def serialize_message(message):
    return {
        "id": message.pk,
        "room_id": message.room_id,
        "sender_id": message.sender_id,
        "sender_username": message.sender.get_username(),
        "text": message.text,
        "timestamp": message.timestamp.isoformat(),
        "is_read": message.is_read,
        "attachments": [serialize_attachment(attachment) for attachment in message.attachments.all()],
    }

def recent_messages_cache_key(room_id):
    return f"admin_chat:room:{room_id}:recent_messages:v2"


def serialize_compact_message(row):
    return {
        "id": row["id"],
        "room_id": row["room_id"],
        "sender_id": row["sender_id"],
        "sender_username": row["sender__username"],
        "sender": row["sender_id"],
        "text": row["text"],
        "timestamp": row["timestamp"].isoformat(),
        "created_at": row["timestamp"].isoformat(),
        "is_read": row["is_read"],
        "attachments": [],
    }


def fetch_recent_messages(room_id, limit=RECENT_MESSAGES_LIMIT, before_id=None):
    queryset = ChatMessage.objects.filter(room_id=room_id)
    if before_id:
        queryset = queryset.filter(pk__lt=before_id)

    rows = list(
        queryset.order_by("-id")
        .values("id", "room_id", "text", "timestamp", "sender_id", "sender__username", "is_read")[: limit + 1]
    )
    has_next = len(rows) > limit
    rows = rows[:limit]
    return [serialize_compact_message(row) for row in reversed(rows)], has_next


def get_cached_recent_messages(room_id):
    cache_key = recent_messages_cache_key(room_id)
    cached = cache.get(cache_key)
    if cached is not None:
        return cached
    messages, has_next = fetch_recent_messages(room_id)
    payload = {"messages": messages, "has_next": has_next}
    cache.set(cache_key, payload, RECENT_MESSAGES_CACHE_TIMEOUT)
    return payload


def get_staff_room_or_404(user, room_id):
    room = get_object_or_404(ChatRoom, pk=room_id)
    if not room.user_can_access(user):
        raise PermissionError
    return room


def get_accessible_rooms(user):
    return (
        ChatRoom.objects.filter(Q(room_type=ChatRoom.GROUP) | Q(room_type=ChatRoom.PRIVATE, participants=user))
        .distinct()
        .order_by("-created_at")
    )


@staff_required
@require_GET
def chat_dashboard(request, room_id=None):
    rooms = list(get_accessible_rooms(request.user))
    if not rooms:
        default_room = ChatRoom.objects.create(name="گفتگوی عمومی", room_type=ChatRoom.GROUP)
        rooms = [default_room]

    if room_id:
        selected_room = get_staff_room_or_404(request.user, room_id)
    else:
        selected_room = rooms[0]

    return render(
        request,
        "admin_chat/chat_dashboard.html",
        {
            "rooms": rooms,
            "selected_room": selected_room,
            "chat_upload_chunk_size": getattr(settings, "CHAT_UPLOAD_CHUNK_SIZE", 1024 * 1024),
            "chat_max_attachment_size": getattr(settings, "CHAT_MAX_ATTACHMENT_SIZE", 300 * 1024 * 1024),
        },
    )


@staff_required
@require_GET
def room_list(request):
    rooms = []
    for room in get_accessible_rooms(request.user):
        rooms.append(
            {
                "id": room.pk,
                "name": room.name,
                "room_type": room.room_type,
                "created_at": room.created_at.isoformat(),
            }
        )
    return JsonResponse({"rooms": rooms})


@staff_required
@require_GET
def message_list(request, room_id):
    try:
        get_staff_room_or_404(request.user, room_id)
    except PermissionError:
        return JsonResponse({"error": "دسترسی غیرمجاز."}, status=403)

    before_id = request.GET.get("before_id")
    try:
        before_id = int(before_id) if before_id else None
    except ValueError:
        before_id = None

    if before_id is None:
        payload = get_cached_recent_messages(room_id)
        messages = payload["messages"]
        has_next = payload["has_next"]
    else:
        messages, has_next = fetch_recent_messages(room_id, before_id=before_id)

    return JsonResponse(
        {
            "messages": messages,
            "limit": RECENT_MESSAGES_LIMIT,
            "has_next": has_next,
        }
    )


@staff_required
@require_GET
def attachment_file(request, pk):
    attachment = get_object_or_404(
        MessageAttachment.objects.select_related("message__room"),
        pk=pk,
    )
    if not attachment.message.room.user_can_access(request.user):
        return JsonResponse({"success": False, "error": "دسترسی غیرمجاز."}, status=403)
    if not attachment.file:
        raise Http404

    try:
        file_handle = attachment.file.open("rb")
    except FileNotFoundError as exc:
        raise Http404 from exc

    content_type = (
        attachment.content_type
        or mimetypes.guess_type(attachment.original_filename or attachment.file.name)[0]
        or "application/octet-stream"
    )
    is_inline_preview = content_type.lower().startswith("image/")
    response = FileResponse(
        file_handle,
        content_type=content_type,
        as_attachment=not is_inline_preview,
        filename=os.path.basename(attachment.original_filename or attachment.file.name),
    )
    response["X-Content-Type-Options"] = "nosniff"
    return response


@staff_required
@require_POST
def upload_chunk(request):
    form = ChunkUploadForm(request.POST, request.FILES)
    if not form.is_valid():
        return JsonResponse({"success": False, "errors": form.errors}, status=400)

    data = form.cleaned_data
    try:
        room = get_staff_room_or_404(request.user, data["room_id"])
    except PermissionError:
        return JsonResponse({"success": False, "error": "دسترسی غیرمجاز."}, status=403)

    message = get_object_or_404(
        ChatMessage.objects.select_related("room", "sender"),
        pk=data["message_id"],
        room=room,
    )
    if message.sender_id != request.user.pk:
        return JsonResponse({"success": False, "error": "فقط فرستنده پیام می‌تواند فایل ضمیمه کند."}, status=403)

    chunk_dir = get_chunk_dir(request.user.pk, data["upload_id"])
    chunk_dir.mkdir(parents=True, exist_ok=True)
    chunk_path = chunk_dir / f"{data['chunk_index']:08d}.part"

    with chunk_path.open("wb") as destination:
        for item in data["chunk"].chunks():
            destination.write(item)

    received_chunks = len(list(chunk_dir.glob("*.part")))
    if received_chunks < data["total_chunks"]:
        return JsonResponse(
            {
                "success": True,
                "complete": False,
                "received_chunks": received_chunks,
                "total_chunks": data["total_chunks"],
            }
        )

    try:
        attachment = assemble_attachment(
            message=message,
            chunk_dir=chunk_dir,
            file_name=data["file_name"],
            file_size=data["file_size"],
            total_chunks=data["total_chunks"],
            content_type=data.get("file_type") or getattr(data["chunk"], "content_type", ""),
        )
    except ValueError as exc:
        return JsonResponse({"success": False, "error": str(exc)}, status=400)

    payload = serialize_attachment(attachment)
    cache.delete(recent_messages_cache_key(room.pk))
    broadcast_attachment(room.pk, message.pk, payload)
    return JsonResponse({"success": True, "complete": True, "attachment": payload})


def get_chunk_dir(user_id, upload_id):
    safe_upload_id = "".join(char for char in upload_id if char.isalnum() or char in ("-", "_"))[:80]
    return Path(settings.MEDIA_ROOT) / "chat_upload_chunks" / str(user_id) / safe_upload_id


@transaction.atomic
def assemble_attachment(message, chunk_dir, file_name, file_size, total_chunks, content_type):
    validate_clean_text(file_name)
    now = timezone.localtime()
    upload_dir = Path(settings.MEDIA_ROOT) / "chat_uploads" / now.strftime("%Y") / now.strftime("%m") / now.strftime("%d")
    upload_dir.mkdir(parents=True, exist_ok=True)
    safe_name = f"{uuid4().hex}_{os.path.basename(file_name)}"
    final_path = upload_dir / safe_name

    with final_path.open("wb") as final_file:
        for index in range(total_chunks):
            chunk_path = chunk_dir / f"{index:08d}.part"
            if not chunk_path.exists():
                raise ValueError("یک یا چند تکه فایل دریافت نشده است.")
            with chunk_path.open("rb") as chunk_file:
                shutil.copyfileobj(chunk_file, final_file)

    actual_size = final_path.stat().st_size
    if actual_size != file_size:
        final_path.unlink(missing_ok=True)
        shutil.rmtree(chunk_dir, ignore_errors=True)
        raise ValueError("حجم فایل نهایی با مقدار اعلام‌شده برابر نیست.")

    relative_path = final_path.relative_to(settings.MEDIA_ROOT).as_posix()
    attachment = MessageAttachment.objects.create(
        message=message,
        file=relative_path,
        original_filename=os.path.basename(file_name),
        content_type=content_type or "application/octet-stream",
        size=actual_size,
    )
    shutil.rmtree(chunk_dir, ignore_errors=True)
    return attachment


def broadcast_attachment(room_id, message_id, attachment_payload):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"admin_chat_{room_id}",
        {
            "type": "attachment_added",
            "message_id": message_id,
            "attachment": attachment_payload,
        },
    )
