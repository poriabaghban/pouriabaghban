import logging
import os
from datetime import timedelta

import jwt
from django.conf import settings
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import F
from django.db.models import Q
from django.http import FileResponse, HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET

from .models import Podcast

logger = logging.getLogger(__name__)


def record_podcast_hit(request, podcast):
    if not podcast or not podcast.pk:
        return False
    try:
        Podcast.objects.filter(pk=podcast.pk).update(views=F("views") + 1)
        podcast.views = (podcast.views or 0) + 1
        return True
    except Exception:
        logger.exception("Could not record podcast hit for %s", podcast.pk)
        return False


def get_watermark_name(request):
    return request.user.username if request.user.is_authenticated else "guest"


def get_audio_content_type(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    return {
        ".mp3": "audio/mpeg",
        ".wav": "audio/wav",
        ".ogg": "audio/ogg",
        ".m4a": "audio/mp4",
        ".flac": "audio/flac",
        ".aac": "audio/aac",
    }.get(ext, "audio/mpeg")


def has_special_poem_access(request):
    return request.user.is_authenticated and request.session.get("sheerwizhe_authenticated") is True


def special_login_required(view_func):
    def wrapped(request, *args, **kwargs):
        if has_special_poem_access(request):
            return view_func(request, *args, **kwargs)
        login_url = f"/sheerwizhe/login/?next={request.get_full_path()}"
        return redirect(login_url)

    return wrapped


def get_podcasts_queryset(content_type):
    return Podcast.objects.filter(is_published=True, content_type=content_type).order_by("-created_at")


def can_access_podcast_audio(request, podcast):
    if podcast.content_type == Podcast.CONTENT_SPECIAL:
        return has_special_poem_access(request)
    return request.user.is_authenticated


def render_podcast_list(request, content_type, template_context):
    podcasts = get_podcasts_queryset(content_type)
    search_query = request.GET.get("search", "").strip()
    if search_query:
        podcasts = podcasts.filter(
            Q(title__icontains=search_query)
            | Q(speaker__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(transcript__icontains=search_query)
        )

    paginator = Paginator(podcasts, 10)
    podcasts_page = paginator.get_page(request.GET.get("page", 1))
    for podcast in podcasts_page:
        record_podcast_hit(request, podcast)

    context = {
        "podcasts": podcasts_page,
        "search_query": search_query,
        "watermark_name": get_watermark_name(request),
    }
    context.update(template_context)
    return render(request, "podcast_app/podcast_list.html", context)


def render_podcast_detail(request, podcast_id, content_type, template_context):
    podcast = get_object_or_404(get_podcasts_queryset(content_type), id=podcast_id)
    record_podcast_hit(request, podcast)

    context = {
        "podcast": podcast,
        "watermark_name": get_watermark_name(request),
    }
    context.update(template_context)
    return render(request, "podcast_app/podcast_detail.html", context)


@login_required(login_url="podcast_app:login")
@require_GET
def podcast_list(request):
    return render_podcast_list(
        request,
        Podcast.CONTENT_REGULAR,
        {
            "section_title": "\u0634\u0639\u0631",
            "list_url_name": "podcast_app:sheer_list",
            "detail_url_name": "podcast_app:podcast_detail",
            "login_url_name": "podcast_app:login",
            "list_path": "/sheer/",
        },
    )


@login_required(login_url="podcast_app:login")
@require_GET
def podcast_detail(request, podcast_id):
    return render_podcast_detail(
        request,
        podcast_id,
        Podcast.CONTENT_REGULAR,
        {
            "list_url_name": "podcast_app:sheer_list",
            "detail_url_name": "podcast_app:podcast_detail",
            "back_label": "\u0628\u0627\u0632\u06af\u0634\u062a \u0628\u0647 \u0634\u0639\u0631\u0647\u0627",
        },
    )


@special_login_required
@require_GET
def special_poem_list(request):
    return render_podcast_list(
        request,
        Podcast.CONTENT_SPECIAL,
        {
            "section_title": "\u0634\u0639\u0631 \u0648\u06cc\u0698\u0647",
            "list_url_name": "podcast_app:special_list",
            "detail_url_name": "podcast_app:special_detail",
            "login_url_name": "podcast_app:special_login",
            "list_path": "/sheerwizhe/",
        },
    )


@special_login_required
@require_GET
def special_poem_detail(request, podcast_id):
    return render_podcast_detail(
        request,
        podcast_id,
        Podcast.CONTENT_SPECIAL,
        {
            "list_url_name": "podcast_app:special_list",
            "detail_url_name": "podcast_app:special_detail",
            "back_label": "\u0628\u0627\u0632\u06af\u0634\u062a \u0628\u0647 \u0634\u0639\u0631 \u0648\u06cc\u0698\u0647",
        },
    )


def special_login(request):
    next_url = request.GET.get("next") or request.POST.get("next") or "/sheerwizhe/"
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            request.session["sheerwizhe_authenticated"] = True
            return redirect(next_url)
    else:
        form = AuthenticationForm(request)

    return render(
        request,
        "podcast_app/login.html",
        {
            "form": form,
            "next": next_url,
            "login_title": "\u0648\u0631\u0648\u062f \u0628\u0647 sheerwizhe",
        },
    )


def special_logout(request):
    request.session.pop("sheerwizhe_authenticated", None)
    return redirect("/")


@login_required(login_url="podcast_app:login")
@require_GET
def generate_audio_token(request, podcast_id):
    podcast = get_object_or_404(Podcast.objects.filter(is_published=True), id=podcast_id)
    if not can_access_podcast_audio(request, podcast):
        return JsonResponse({"success": False, "error": "\u0628\u0631\u0627\u06cc \u067e\u062e\u0634 \u0641\u0627\u06cc\u0644 \u0635\u0648\u062a\u06cc \u0628\u0627\u06cc\u062f \u0631\u0648\u06cc \u067e\u0633\u062a \u06a9\u0644\u06cc\u06a9 \u06a9\u0646\u06cc\u062f."}, status=403)
    if not podcast.audio_file:
        return JsonResponse({"success": False, "error": "فایل صوتی وجود ندارد."}, status=404)

    file_path = podcast.audio_file.path
    if not os.path.exists(file_path):
        return JsonResponse({"success": False, "error": "فایل صوتی پیدا نشد."}, status=404)

    expiration_seconds = getattr(settings, "JWT_EXPIRATION", 300)
    expires_at = timezone.now() + timedelta(seconds=expiration_seconds)
    payload = {
        "user_id": request.user.id,
        "username": request.user.username,
        "podcast_id": podcast.id,
        "content_type": podcast.content_type,
        "exp": int(expires_at.timestamp()),
        "iat": int(timezone.now().timestamp()),
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    return JsonResponse(
        {
            "success": True,
            "token": token,
            "expires_in": expiration_seconds,
            "expires_at": expires_at.isoformat(),
            "title": podcast.title,
            "speaker": podcast.speaker,
            "file_size": podcast.get_file_size(),
            "extension": podcast.get_file_extension(),
        }
    )


@login_required(login_url="podcast_app:login")
@never_cache
@require_GET
def secure_audio_stream(request, podcast_id):
    token = request.GET.get("token")
    if not token:
        return HttpResponseForbidden("\u0628\u0631\u0627\u06cc \u067e\u062e\u0634 \u0641\u0627\u06cc\u0644 \u0635\u0648\u062a\u06cc \u0628\u0627\u06cc\u062f \u0631\u0648\u06cc \u067e\u0633\u062a \u06a9\u0644\u06cc\u06a9 \u06a9\u0646\u06cc\u062f.")

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        if payload.get("user_id") != request.user.id:
            return HttpResponseForbidden("دسترسی غیرمجاز.")
        if payload.get("podcast_id") != podcast_id:
            return HttpResponseForbidden("دسترسی غیرمجاز.")
    except jwt.ExpiredSignatureError:
        return HttpResponseForbidden("توکن منقضی شده است.")
    except jwt.InvalidTokenError:
        return HttpResponseForbidden("توکن نامعتبر است.")

    podcast = get_object_or_404(Podcast.objects.filter(is_published=True), id=podcast_id)
    if not can_access_podcast_audio(request, podcast):
        return HttpResponseForbidden("\u0628\u0631\u0627\u06cc \u067e\u062e\u0634 \u0641\u0627\u06cc\u0644 \u0635\u0648\u062a\u06cc \u0628\u0627\u06cc\u062f \u0631\u0648\u06cc \u067e\u0633\u062a \u06a9\u0644\u06cc\u06a9 \u06a9\u0646\u06cc\u062f.")
    if payload.get("content_type") != podcast.content_type:
        return HttpResponseForbidden("دسترسی غیرمجاز.")
    if not podcast.audio_file or not os.path.exists(podcast.audio_file.path):
        return HttpResponseForbidden("فایل صوتی پیدا نشد.")

    file_path = podcast.audio_file.path
    file_size = os.path.getsize(file_path)
    content_type = get_audio_content_type(file_path)
    range_header = request.headers.get("Range")

    if range_header:
        try:
            range_value = range_header.replace("bytes=", "", 1)
            start_text, end_text = range_value.split("-", 1)
            start = int(start_text) if start_text else 0
            end = int(end_text) if end_text else file_size - 1
            end = min(end, file_size - 1)
            length = end - start + 1
            with open(file_path, "rb") as audio:
                audio.seek(start)
                data = audio.read(length)
            response = HttpResponse(data, status=206, content_type=content_type)
            response["Content-Range"] = f"bytes {start}-{end}/{file_size}"
            response["Content-Length"] = str(length)
        except Exception:
            response = FileResponse(open(file_path, "rb"), content_type=content_type)
            response["Content-Length"] = str(file_size)
    else:
        response = FileResponse(open(file_path, "rb"), content_type=content_type)
        response["Content-Length"] = str(file_size)

    response["Content-Disposition"] = 'inline; filename="podcast-audio"'
    response["Accept-Ranges"] = "bytes"
    response["X-Content-Type-Options"] = "nosniff"
    response["Cache-Control"] = "private, no-cache, no-store, must-revalidate"
    response["Pragma"] = "no-cache"
    response["Expires"] = "0"
    return response
