import mimetypes
import os
from datetime import timedelta
from math import ceil

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.core.exceptions import PermissionDenied
from django.db import models
from django.db.models import Count, Q
from django.http import FileResponse, Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import DownloadCommentForm, FrontendLoginForm
from .models import DownloadCategory, DownloadItem, DownloadLog, DownloadPageSetting, DownloadReaction

DOWNLOAD_COOLDOWN_SECONDS = 7
DETAIL_ACCESS_SESSION_KEY = "download_detail_access"


def get_client_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def active_items():
    return DownloadItem.objects.filter(is_active=True, category__is_active=True).select_related("category")


def mark_detail_access(request, item):
    access_map = request.session.get(DETAIL_ACCESS_SESSION_KEY, {})
    access_map[str(item.pk)] = timezone.now().timestamp()
    request.session[DETAIL_ACCESS_SESSION_KEY] = access_map
    request.session.modified = True


def has_detail_access(request, item):
    access_map = request.session.get(DETAIL_ACCESS_SESSION_KEY, {})
    return str(item.pk) in access_map


def latest_download_for_request(request):
    logs = DownloadLog.objects.all()
    if request.user.is_authenticated:
        logs = logs.filter(user=request.user)
    else:
        client_ip = get_client_ip(request)
        if not client_ip:
            return None
        logs = logs.filter(user__isnull=True, ip_address=client_ip)
    return logs.order_by("-downloaded_at").first()


def download_cooldown_remaining(request):
    latest_log = latest_download_for_request(request)
    if not latest_log:
        return 0
    available_at = latest_log.downloaded_at + timedelta(seconds=DOWNLOAD_COOLDOWN_SECONDS)
    remaining = (available_at - timezone.now()).total_seconds()
    return max(0, ceil(remaining))


def downloads_home(request):
    items = active_items()
    grouped = {
        DownloadItem.ANDROID: items.filter(platform=DownloadItem.ANDROID),
        DownloadItem.WINDOWS: items.filter(platform=DownloadItem.WINDOWS),
        DownloadItem.CONFIG: items.filter(platform=DownloadItem.CONFIG),
        DownloadItem.OTHER: items.filter(platform=DownloadItem.OTHER),
    }
    return render(request, "downloads/download_list.html", {"grouped_items": grouped})


def category_detail(request, slug):
    category = get_object_or_404(DownloadCategory, slug=slug, is_active=True)
    category_items = active_items().filter(category=category)
    return render(
        request,
        "downloads/category_detail.html",
        {"category": category, "items": category_items},
    )


def item_detail(request, slug):
    item = get_object_or_404(active_items(), slug=slug)
    mark_detail_access(request, item)
    settings_obj = DownloadPageSetting.get_solo()
    comment_form = DownloadCommentForm()

    if request.method == "POST":
        if not settings_obj.comments_enabled:
            messages.error(request, "Comments are disabled.")
            return redirect("downloads:item_detail", slug=item.slug)
        comment_form = DownloadCommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.download_item = item
            comment.user = request.user if request.user.is_authenticated else None
            comment.ip_address = get_client_ip(request)
            comment.user_agent = request.META.get("HTTP_USER_AGENT", "")[:1000]
            comment.is_approved = not settings_obj.comment_moderation_enabled
            comment.save()
            if settings_obj.comment_moderation_enabled:
                messages.success(request, "Comment saved and is waiting for admin approval.")
            else:
                messages.success(request, "Comment saved.")
            return redirect("downloads:item_detail", slug=item.slug)

    comments = item.comments.filter(is_active=True, is_approved=True).select_related("user")
    reaction_counts = item.reactions.values("reaction_type").annotate(total=Count("id"))
    counts = {row["reaction_type"]: row["total"] for row in reaction_counts}
    user_reaction = None
    if request.user.is_authenticated:
        user_reaction = item.reactions.filter(user=request.user).first()
    elif request.session.session_key:
        user_reaction = item.reactions.filter(user__isnull=True, session_key=request.session.session_key).first()

    return render(
        request,
        "downloads/item_detail.html",
        {
            "item": item,
            "settings_obj": settings_obj,
            "comment_form": comment_form,
            "comments": comments,
            "like_count": counts.get(DownloadReaction.LIKE, 0),
            "broken_heart_count": counts.get(DownloadReaction.BROKEN_HEART, 0),
            "user_reaction": user_reaction.reaction_type if user_reaction else "",
        },
    )


def download_file(request, slug):
    item = get_object_or_404(active_items(), slug=slug)
    if not has_detail_access(request, item):
        messages.info(request, "Please open the file details before downloading.")
        return redirect("downloads:item_detail", slug=item.slug)

    remaining_seconds = download_cooldown_remaining(request)
    if remaining_seconds:
        messages.warning(request, f"Please wait {remaining_seconds} seconds before downloading again.")
        return redirect("downloads:item_detail", slug=item.slug)

    if item.requires_login and not request.user.is_authenticated:
        login_url = reverse("downloads:login")
        return redirect(f"{login_url}?next={request.get_full_path()}")
    if not item.user_can_download(request.user):
        raise PermissionDenied
    if not item.file:
        raise Http404

    DownloadItem.objects.filter(pk=item.pk).update(download_count=models.F("download_count") + 1)
    DownloadLog.objects.create(
        user=request.user if request.user.is_authenticated else None,
        download_item=item,
        ip_address=get_client_ip(request),
        user_agent=request.META.get("HTTP_USER_AGENT", "")[:1000],
    )

    file_handle = item.file.open("rb")
    content_type = mimetypes.guess_type(item.file.name)[0] or "application/octet-stream"
    response = FileResponse(file_handle, content_type=content_type, as_attachment=True, filename=os.path.basename(item.file.name))
    response["X-Content-Type-Options"] = "nosniff"
    return response


@require_POST
def react(request, slug):
    item = get_object_or_404(active_items(), slug=slug)
    settings_obj = DownloadPageSetting.get_solo()
    if not settings_obj.reactions_enabled:
        return JsonResponse({"success": False, "error": "Reactions are disabled."}, status=403)

    reaction_type = request.POST.get("reaction_type")
    if reaction_type not in dict(DownloadReaction.REACTION_CHOICES):
        return JsonResponse({"success": False, "error": "Invalid reaction type."}, status=400)

    if request.user.is_authenticated:
        reaction, _created = DownloadReaction.objects.get_or_create(
            download_item=item,
            user=request.user,
            defaults={
                "reaction_type": reaction_type,
                "ip_address": get_client_ip(request),
                "user_agent": request.META.get("HTTP_USER_AGENT", "")[:1000],
            },
        )
    else:
        if not request.session.session_key:
            request.session.create()
        reaction, _created = DownloadReaction.objects.get_or_create(
            download_item=item,
            user=None,
            session_key=request.session.session_key,
            defaults={
                "reaction_type": reaction_type,
                "ip_address": get_client_ip(request),
                "user_agent": request.META.get("HTTP_USER_AGENT", "")[:1000],
            },
        )

    if reaction.reaction_type != reaction_type:
        reaction.reaction_type = reaction_type
        reaction.ip_address = get_client_ip(request)
        reaction.user_agent = request.META.get("HTTP_USER_AGENT", "")[:1000]
        reaction.save(update_fields=("reaction_type", "ip_address", "user_agent", "updated_at"))

    counts = item.reactions.values("reaction_type").annotate(total=Count("id"))
    count_map = {row["reaction_type"]: row["total"] for row in counts}
    return JsonResponse(
        {
            "success": True,
            "reaction_type": reaction_type,
            "like_count": count_map.get(DownloadReaction.LIKE, 0),
            "broken_heart_count": count_map.get(DownloadReaction.BROKEN_HEART, 0),
        }
    )


class FrontendLoginView(LoginView):
    template_name = "registration/login.html"
    authentication_form = FrontendLoginForm
    redirect_authenticated_user = True

    def get_success_url(self):
        redirect_to = self.get_redirect_url()
        if redirect_to:
            return redirect_to
        return reverse("downloads:dashboard")


@login_required
def dashboard(request):
    accessible = active_items()
    if not (request.user.is_staff or request.user.is_superuser):
        accessible = accessible.filter(
            Q(requires_login=False)
            | Q(allowed_users=request.user)
            | Q(allowed_groups__in=request.user.groups.all())
            | (Q(requires_login=True) & Q(allowed_users__isnull=True) & Q(allowed_groups__isnull=True))
        ).distinct()
    logs = DownloadLog.objects.filter(user=request.user).select_related("download_item")[:10]
    return render(request, "downloads/dashboard.html", {"items": accessible, "logs": logs})


@login_required
def frontend_logout(request):
    logout(request)
    return redirect("downloads:login")
