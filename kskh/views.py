import json
import mimetypes
import os
from pathlib import Path
from functools import wraps
from math import ceil

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Count
from django.http import FileResponse, Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.views.decorators.http import require_POST
from rest_framework_simplejwt.tokens import RefreshToken

from .forms import KskhCommentForm, KskhLoginForm, KskhPostForm
from .models import KskhComment, KskhPost, KskhReaction


User = get_user_model()

KSKH_SESSION_KEY = "kskh_authenticated"
KSKH_USER_ID_KEY = "kskh_user_id"
KSKH_DETAIL_ACCESS_KEY = "kskh_detail_access"
KSKH_DOWNLOAD_COOLDOWN_KEY = "kskh_last_download_at"
KSKH_DOWNLOAD_COOLDOWN_SECONDS = 7


def has_kskh_access(request):
    return request.session.get(KSKH_SESSION_KEY) is True and bool(request.session.get(KSKH_USER_ID_KEY))


def get_kskh_user(request):
    user_id = request.session.get(KSKH_USER_ID_KEY)

    if not user_id:
        return None

    try:
        return User.objects.get(pk=user_id, is_active=True)
    except User.DoesNotExist:
        request.session.pop(KSKH_SESSION_KEY, None)
        request.session.pop(KSKH_USER_ID_KEY, None)
        return None


def safe_next_url(request, fallback=None):
    fallback = fallback or reverse("kskh:index")
    next_url = request.GET.get("next") or request.POST.get("next") or fallback

    if url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return next_url

    return fallback


def kskh_login_required(view_func):
    @wraps(view_func)
    def wrapped(request, *args, **kwargs):
        if has_kskh_access(request) and get_kskh_user(request):
            return view_func(request, *args, **kwargs)

        login_url = reverse("kskh:login")
        return redirect(f"{login_url}?next={request.get_full_path()}")

    return wrapped


def kskh_template_context(request, **extra):
    kskh_user = get_kskh_user(request)

    context = {
        "kskh_is_authenticated": bool(kskh_user),
        "kskh_user": kskh_user,
        "kskh_username": kskh_user.get_username() if kskh_user else "",
    }

    context.update(extra)
    return context


def get_client_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")

    if forwarded:
        return forwarded.split(",")[0].strip()

    return request.META.get("REMOTE_ADDR")


def active_posts():
    return (
        KskhPost.objects
        .filter(is_active=True)
        .select_related("uploaded_by")
        .order_by("-pk")
    )


def latest_config_post():
    return (
        active_posts()
        .filter(kind=KskhPost.CONFIG)
        .exclude(file="")
        .exclude(file__isnull=True)
        .first()
    )


def mark_detail_access(request, post):
    access_map = request.session.get(KSKH_DETAIL_ACCESS_KEY, {})
    access_map[str(post.pk)] = timezone.now().timestamp()
    request.session[KSKH_DETAIL_ACCESS_KEY] = access_map
    request.session.modified = True


def has_detail_access(request, post):
    access_map = request.session.get(KSKH_DETAIL_ACCESS_KEY, {})
    return str(post.pk) in access_map


def download_cooldown_remaining(request):
    last_download_at = request.session.get(KSKH_DOWNLOAD_COOLDOWN_KEY)

    if not last_download_at:
        return 0

    available_at = last_download_at + KSKH_DOWNLOAD_COOLDOWN_SECONDS
    remaining = available_at - timezone.now().timestamp()

    return max(0, ceil(remaining))


def mark_download(request):
    request.session[KSKH_DOWNLOAD_COOLDOWN_KEY] = timezone.now().timestamp()
    request.session.modified = True


def open_post_file(post):
    if not post or not post.file:
        raise Http404("فایلی برای دانلود وجود ندارد.")

    try:
        if post.file.storage.exists(post.file.name):
            return post.file.open("rb")
    except Exception:
        pass

    relative_name = Path(post.file.name)

    possible_roots = [
        Path(settings.MEDIA_ROOT),
        Path(settings.BASE_DIR) / "public" / "media",
        Path(settings.BASE_DIR) / "media",
    ]

    for root in possible_roots:
        candidate = root / relative_name

        if candidate.exists() and candidate.is_file():
            return candidate.open("rb")

    raise Http404("فایل روی سرور پیدا نشد.")


def post_file_size_text(post):
    try:
        value = post.file_size_display
        if callable(value):
            return value()
        return value or ""
    except Exception:
        return ""


@kskh_login_required
def index(request):
    search_query = (request.GET.get("q") or "").strip()

    posts = active_posts().annotate(
        like_total=Count(
            "reactions",
            filter=models.Q(reactions__reaction_type=KskhReaction.LIKE),
        ),
        dislike_total=Count(
            "reactions",
            filter=models.Q(reactions__reaction_type=KskhReaction.DISLIKE),
        ),
    )

    apk_posts = posts.filter(file_extension__in=[".apk", ".apks", ".aab", ".xapk"])
    exe_posts = posts.filter(file_extension=".exe")
    config_posts = posts.filter(kind=KskhPost.CONFIG)

    if search_query:
        posts = posts.filter(
            models.Q(title__icontains=search_query)
            | models.Q(description__icontains=search_query)
            | models.Q(file_extension__icontains=search_query)
            | models.Q(file__icontains=search_query)
            | models.Q(kind__icontains=search_query)
        )

    # Ajax live search: template can call /kskh/?q=... with X-Requested-With=XMLHttpRequest
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        results = []

        for post in posts[:30]:
            results.append(
                {
                    "id": post.pk,
                    "slug": post.slug,
                    "title": post.title,
                    "description": post.description or "",
                    "kind": post.kind,
                    "file_extension": post.file_extension or "",
                    "file_size": post_file_size_text(post),
                    "download_count": post.download_count,
                    "like_count": getattr(post, "like_total", 0) or 0,
                    "dislike_count": getattr(post, "dislike_total", 0) or 0,
                    "detail_url": reverse("kskh:detail", kwargs={"slug": post.slug}),
                    "download_url": reverse("kskh:download", kwargs={"slug": post.slug}),
                    "react_url": reverse("kskh:react", kwargs={"slug": post.slug}),
                }
            )

        return JsonResponse(
            {
                "success": True,
                "query": search_query,
                "count": posts.count(),
                "results": results,
                "reaction_message": "دانلود شروع شد. بعد از دانلود لطفاً برای فایل ری‌اکشن بگذارید.",
            }
        )

    return render(
        request,
        "kskh/index.html",
        kskh_template_context(
            request,
            posts=posts,
            search_query=search_query,
            latest_apk=apk_posts.first(),
            latest_exe=exe_posts.first(),
            latest_config=config_posts.first(),
            apk_posts=apk_posts[:3],
            exe_posts=exe_posts[:3],
            config_posts=config_posts[:3],
        ),
    )


@kskh_login_required
def detail(request, slug):
    post = get_object_or_404(active_posts(), slug=slug)

    mark_detail_access(request, post)

    if request.method == "GET" and request.GET.get("download") == "1":
        return redirect("kskh:download", slug=post.slug)

    comment_form = KskhCommentForm()
    kskh_user = get_kskh_user(request)

    if request.method == "POST":
        comment_form = KskhCommentForm(request.POST)

        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.user = kskh_user

            parent_id = comment_form.cleaned_data.get("parent_id")

            if parent_id:
                comment.parent = get_object_or_404(
                    KskhComment,
                    pk=parent_id,
                    post=post,
                    parent__isnull=True,
                    is_active=True,
                    is_approved=True,
                )

            comment.is_approved = True
            comment.save()

            messages.success(request, "کامنت ثبت شد.")
            return redirect("kskh:detail", slug=post.slug)

    root_comments = (
        post.comments
        .filter(parent__isnull=True, is_active=True, is_approved=True)
        .select_related("user")
        .prefetch_related("replies__user")
    )

    reaction_counts = post.reactions.values("reaction_type").annotate(total=Count("id"))
    counts = {row["reaction_type"]: row["total"] for row in reaction_counts}

    user_reaction = post.reactions.filter(user=kskh_user).first() if kskh_user else None

    return render(
        request,
        "kskh/detail.html",
        kskh_template_context(
            request,
            post=post,
            comment_form=comment_form,
            comments=root_comments,
            like_count=counts.get(KskhReaction.LIKE, 0),
            dislike_count=counts.get(KskhReaction.DISLIKE, 0),
            user_reaction=user_reaction.reaction_type if user_reaction else "",
            auto_download=False,
        ),
    )


@kskh_login_required
def upload(request):
    form = KskhPostForm(request.POST or None, request.FILES or None)

    if request.method == "POST" and form.is_valid():
        post = form.save(commit=False)
        post.uploaded_by = get_kskh_user(request)

        # فایل اول باید برود برای تایید ادمین
        # تا وقتی ادمین تایید نکند، در پنل کاربر نمایش داده نمی‌شود
        post.is_active = False

        post.save()

        messages.success(
            request,
            "فایل شما با موفقیت ارسال شد و بعد از تایید ادمین نمایش داده می‌شود."
        )

        return redirect("kskh:index")

    return render(
        request,
        "kskh/upload.html",
        kskh_template_context(request, form=form)
    )


@kskh_login_required
def download_file(request, slug):
    requested_post = active_posts().filter(slug=slug).first()

    if requested_post and requested_post.file:
        post = requested_post
    else:
        post = latest_config_post()

    if not post:
        messages.error(request, "هیچ فایلی برای دانلود وجود ندارد.")
        return redirect("kskh:index")

    remaining_seconds = download_cooldown_remaining(request)

    if remaining_seconds:
        messages.warning(request, f"برای دانلود بعدی {remaining_seconds} ثانیه صبر کنید.")

        if requested_post:
            return redirect("kskh:detail", slug=requested_post.slug)

        return redirect("kskh:index")

    try:
        file_handle = open_post_file(post)
    except Http404:
        fallback_post = latest_config_post()

        if fallback_post and fallback_post.pk != post.pk:
            try:
                post = fallback_post
                file_handle = open_post_file(post)
            except Http404:
                messages.error(request, "فایل روی سرور پیدا نشد.")
                return redirect("kskh:index")
        else:
            messages.error(request, "فایل روی سرور پیدا نشد.")
            return redirect("kskh:index")

    KskhPost.objects.filter(pk=post.pk).update(
        download_count=models.F("download_count") + 1
    )

    mark_download(request)

    content_type = mimetypes.guess_type(post.file.name)[0] or "application/octet-stream"
    filename = os.path.basename(post.file.name)

    response = FileResponse(
        file_handle,
        content_type=content_type,
        as_attachment=True,
        filename=filename,
    )

    response["X-Content-Type-Options"] = "nosniff"
    response["X-Reaction-Reminder"] = "بعد از دانلود لطفاً برای فایل ری‌اکشن بگذارید."

    return response


@require_POST
@kskh_login_required
def react(request, slug):
    post = get_object_or_404(active_posts(), slug=slug)

    reaction_type = request.POST.get("reaction_type")

    if reaction_type not in dict(KskhReaction.REACTION_CHOICES):
        return JsonResponse(
            {
                "success": False,
                "error": "نوع رای معتبر نیست.",
            },
            status=400,
        )

    kskh_user = get_kskh_user(request)

    defaults = {
        "reaction_type": reaction_type,
        "ip_address": get_client_ip(request),
        "user_agent": request.META.get("HTTP_USER_AGENT", "")[:1000],
    }

    reaction, _created = KskhReaction.objects.get_or_create(
        post=post,
        user=kskh_user,
        defaults=defaults,
    )

    if reaction.reaction_type != reaction_type:
        reaction.reaction_type = reaction_type
        reaction.ip_address = defaults["ip_address"]
        reaction.user_agent = defaults["user_agent"]
        reaction.save(
            update_fields=(
                "reaction_type",
                "ip_address",
                "user_agent",
                "updated_at",
            )
        )

    counts = post.reactions.values("reaction_type").annotate(total=Count("id"))
    count_map = {row["reaction_type"]: row["total"] for row in counts}

    return JsonResponse(
        {
            "success": True,
            "reaction_type": reaction_type,
            "like_count": count_map.get(KskhReaction.LIKE, 0),
            "dislike_count": count_map.get(KskhReaction.DISLIKE, 0),
            "message": "ری‌اکشن شما ثبت شد.",
        }
    )


@require_POST
@kskh_login_required
def delete_comment(request, pk):
    comment = get_object_or_404(
        KskhComment,
        pk=pk,
        user=get_kskh_user(request),
        is_approved=True,
        is_active=True,
    )

    slug = comment.post.slug

    comment.is_active = False
    comment.save(update_fields=("is_active", "updated_at"))

    messages.success(request, "کامنت حذف شد.")

    return redirect("kskh:detail", slug=slug)


@never_cache
@ensure_csrf_cookie
def kskh_login(request):
    next_url = safe_next_url(request, reverse("kskh:index"))

    if has_kskh_access(request) and get_kskh_user(request):
        return redirect(next_url)

    if request.method == "POST":
        form = KskhLoginForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()

            login(request, user)

            request.session[KSKH_SESSION_KEY] = True
            request.session[KSKH_USER_ID_KEY] = user.pk

            return redirect(next_url)
    else:
        form = KskhLoginForm(request)

    return render(
        request,
        "kskh/login.html",
        {
            "form": form,
            "next": next_url,
        },
    )


@csrf_exempt
@require_POST
@never_cache
def kskh_api_login(request):
    try:
        if request.content_type == "application/json":
            payload = json.loads(request.body.decode("utf-8") or "{}")
        else:
            payload = request.POST
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse(
            {
                "success": False,
                "error": "Invalid JSON payload.",
            },
            status=400,
        )

    username = (payload.get("username") or "").strip()
    password = payload.get("password") or ""

    user = authenticate(request, username=username, password=password)

    if not user:
        return JsonResponse(
            {
                "success": False,
                "error": "Invalid username or password.",
            },
            status=401,
        )

    if not user.is_active:
        return JsonResponse(
            {
                "success": False,
                "error": "User account is disabled.",
            },
            status=403,
        )

    refresh = RefreshToken.for_user(user)

    return JsonResponse(
        {
            "success": True,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "token_type": "Bearer",
            "user": {
                "id": user.pk,
                "username": user.get_username(),
            },
        }
    )


@kskh_login_required
def kskh_logout(request):
    request.session.pop(KSKH_SESSION_KEY, None)
    request.session.pop(KSKH_USER_ID_KEY, None)

    logout(request)

    return redirect("kskh:login")
