from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
from django.db.models import Q
from django.utils.translation import activate, get_language, gettext as _
from django.views.decorators.csrf import csrf_exempt, csrf_protect, ensure_csrf_cookie
from django.views.generic import TemplateView
from .models import HomePageComment, PageSection, PageContent, SiteSettings, Skill, SocialLink, ErrorPage, Testimonial
from blog.models import BlogPost
from pouriabaghban3.input_validation import FORBIDDEN_USER_INPUT_MESSAGE, contains_forbidden_user_input


COMMENT_RESPONSE_MESSAGES = {
    "fa": {
        "success": "نظر شما با موفقیت ارسال شد",
        "failure": "متاسفانه نظر ارسال نشد مجددا تلاش فرمایید",
    },
    "en": {
        "success": "Your comment was sent successfully.",
        "failure": "Unfortunately, your comment was not sent. Please try again.",
    },
    "de": {
        "success": "Ihr Kommentar wurde erfolgreich gesendet.",
        "failure": "Leider wurde Ihr Kommentar nicht gesendet. Bitte versuchen Sie es erneut.",
    },
}


def get_comment_response_messages():
    language = (get_language() or settings.LANGUAGE_CODE).split("-")[0]
    return COMMENT_RESPONSE_MESSAGES.get(language, COMMENT_RESPONSE_MESSAGES["fa"])


def csrf_failure(request, reason=""):
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse(
            {
                "status": "error",
                "message": get_comment_response_messages()["failure"],
            },
            status=403,
        )
    return render(request, "403.html", status=403)


def language_content_filter(prefixes=("title", "description")):
    language = (get_language() or "fa").split("-")[0]
    suffix = language if language in ("en", "de") else "fa"
    query = Q()
    for prefix in prefixes:
        field = f"{prefix}_{suffix}"
        query &= Q(**{f"{field}__isnull": False}) & ~Q(**{field: ""})
    return query


def blog_language_filter():
    language = (get_language() or "fa").split("-")[0]
    suffix = language if language in ("en", "de") else "fa"
    return (
        Q(**{f"title_{suffix}__isnull": False}) & ~Q(**{f"title_{suffix}": ""})
        & Q(**{f"content_{suffix}__isnull": False}) & ~Q(**{f"content_{suffix}": ""})
        & Q(**{f"excerpt_{suffix}__isnull": False}) & ~Q(**{f"excerpt_{suffix}": ""})
    )

def get_page_sections(page_name):
    """دریافت تمام بخش‌های یک صفحه"""
    return PageSection.objects.filter(page=page_name, is_active=True).filter(language_content_filter()).order_by('order')


def get_home_section_map():
    """Return the first active editable section for each home-page section key."""
    sections = PageSection.objects.filter(page='index', is_active=True).filter(language_content_filter()).order_by('section', 'order')
    section_map = {}
    for section in sections:
        section_map.setdefault(section.section, section)
    return section_map

def get_home_comments():
    """Published comments submitted from the home page."""
    return HomePageComment.objects.filter(is_published=True).order_by('order', '-created_at')
def get_page_content(key):
    """دریافت یک محتوای خاص صفحه"""
    try:
        return PageContent.objects.filter(language_content_filter(("title", "content"))).get(key=key, is_active=True)
    except PageContent.DoesNotExist:
        return None

def get_site_settings():
    """دریافت تنظیمات سایت"""
    return SiteSettings.objects.first()

def get_all_skills():
    """دریافت تمام مهارت‌های فعال"""
    return Skill.objects.filter(is_active=True).order_by('order')

def get_social_links():
    """دریافت تمام لینک‌های اجتماعی"""
    return SocialLink.objects.filter(is_active=True).exclude(platform="git" + "hub")

def get_testimonials():
    """دریافت تمام نظرات منتشر شده"""
    return Testimonial.objects.filter(is_published=True).order_by('order')


def get_homepage_posts():
    """Published blog posts selected for the home-page blog preview."""
    return (
        BlogPost.objects.filter(status='published', is_active=True, is_on_homepage=True)
        .filter(blog_language_filter())
        .select_related('author', 'category')
        .prefetch_related('tags')
        .order_by('-published_at', '-created_at')[:3]
    )


@csrf_protect
def submit_home_comment(request):
    """Store a home-page user comment for admin review."""
    messages = get_comment_response_messages()
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': messages['failure']}, status=405)

    name = (request.POST.get('name') or '').strip()
    email = (request.POST.get('email') or '').strip()
    comment = (request.POST.get('comment') or '').strip()

    if not name or not email or not comment:
        return JsonResponse({'status': 'error', 'message': messages['failure']}, status=400)

    if any(contains_forbidden_user_input(value) for value in (name, email, comment)):
        return JsonResponse({'status': 'error', 'message': FORBIDDEN_USER_INPUT_MESSAGE}, status=400)

    if len(comment) > 500:
        return JsonResponse({'status': 'error', 'message': messages['failure']}, status=400)

    HomePageComment.objects.create(name=name, email=email, comment=comment)
    return JsonResponse({'status': 'ok', 'message': messages['success']})
@csrf_exempt
def set_language_from_storage(request):
    lang_code = request.POST.get('lang') or request.GET.get('lang')
    supported_languages = dict(settings.LANGUAGES)

    if lang_code not in supported_languages:
        return JsonResponse({'status': 'error', 'message': 'Unsupported language'}, status=400)

    activate(lang_code)
    response = JsonResponse({'status': 'ok', 'language': lang_code})
    response.set_cookie(
        settings.LANGUAGE_COOKIE_NAME,
        lang_code,
        max_age=365 * 24 * 60 * 60,
    )
    return response

def testimonials_json(request):
    """Return published testimonials as JSON for front-end polling/append."""
    qs = get_testimonials()
    data = []
    for t in qs:
        data.append({
            'id': t.id,
            'name': t.name,
            'title': t.title or '',
            'message': t.message,
            'image': t.image.url if t.image else None,
            'rating': t.rating,
            'order': t.order,
        })
    return JsonResponse({'testimonials': data})


class HomePageView(TemplateView):
    """صفحه اصلی سایت"""
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_settings'] = get_site_settings()
        context['skills'] = get_all_skills()
        context['social_links'] = get_social_links()
        return context


@ensure_csrf_cookie
def home_page(request):
    """نمای تابع برای صفحه اصلی"""
    context = {
        'site_settings': get_site_settings(),
        'skills': get_all_skills(),
        'social_links': get_social_links(),
        'testimonials': get_testimonials(),
        'home_sections': get_home_section_map(),
        'home_comments': get_home_comments(),
        'latest_posts': get_homepage_posts(),
    }
    return render(request, 'index.html', context)


def error_400(request, exception=None):
    """Handle 400 Bad Request"""
    error = ErrorPage.objects.filter(status_code=400).first()
    context = {
        'status_code': 400,
        'title': error.title if error else _('درخواست نامعتبر'),
        'description': error.description if error else _('متأسفانه، درخواست شما نامعتبر است.'),
        'image': error.image.url if error and error.image else None,
        'button_text': error.button_text if error else _('بازگشت به صفحه اصلی'),
        'button_url': error.button_url if error else '/',
    }
    return render(request, 'error.html', context, status=400)


def error_403(request, exception=None):
    """Handle 403 Forbidden"""
    error = ErrorPage.objects.filter(status_code=403).first()
    context = {
        'status_code': 403,
        'title': error.title if error else _('دسترسی ممنوع'),
        'description': error.description if error else _('شما اجازهٔ دسترسی به این صفحه را ندارید.'),
        'image': error.image.url if error and error.image else None,
        'button_text': error.button_text if error else _('بازگشت به صفحه اصلی'),
        'button_url': error.button_url if error else '/',
    }
    return render(request, 'error.html', context, status=403)


def error_404(request, exception=None):
    """Handle 404 Not Found"""
    error = ErrorPage.objects.filter(status_code=404).first()
    context = {
        'status_code': 404,
        'title': error.title if error else _('صفحه پیدا نشد'),
        'description': error.description if error else _('متأسفانه، صفحه‌ای که دنبال آن می‌گردید پیدا نشد.'),
        'image': error.image.url if error and error.image else None,
        'button_text': error.button_text if error else _('بازگشت به صفحه اصلی'),
        'button_url': error.button_url if error else '/',
    }
    return render(request, 'error.html', context, status=404)


def error_500(request):
    """Handle 500 Internal Server Error"""
    error = ErrorPage.objects.filter(status_code=500).first()
    context = {
        'status_code': 500,
        'title': error.title if error else _('خطای سرور'),
        'description': error.description if error else _('متأسفانه، سرور یک خطا برخورد کرد.'),
        'image': error.image.url if error and error.image else None,
        'button_text': error.button_text if error else _('بازگشت به صفحه اصلی'),
        'button_url': error.button_url if error else '/',
    }
    return render(request, 'error.html', context, status=500)


