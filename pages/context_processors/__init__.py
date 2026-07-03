from django.conf import settings
from django.urls import translate_url
from django.utils import translation

from pages.models import FooterSettings, NavbarItem, SiteSettings, SocialLink


def site_context(request):
    """Return site-wide settings used by the public templates."""
    try:
        site_settings = SiteSettings.objects.first()
    except Exception:
        site_settings = None

    try:
        social_links = SocialLink.objects.filter(is_active=True).exclude(platform="git" + "hub")
    except Exception:
        social_links = []

    current_language = translation.get_language() or settings.LANGUAGE_CODE
    language_code = current_language.split("-")[0]

    try:
        navbar_items = [
            item
            for item in NavbarItem.objects.filter(is_active=True).order_by("order", "title")
            if item.is_available_in_language(language_code)
        ]
    except Exception:
        navbar_items = []

    try:
        footer_settings = FooterSettings.objects.filter(is_active=True).first()
        if footer_settings and not footer_settings.is_available_in_language(language_code):
            footer_settings = None
    except Exception:
        footer_settings = None

    absolute_url = request.build_absolute_uri()
    language_urls = {}
    for language_code, _language_name in settings.LANGUAGES:
        with translation.override(language_code):
            language_urls[language_code] = translate_url(absolute_url, language_code)

    return {
        "site_settings": site_settings,
        "social_links": social_links,
        "navbar_items": navbar_items,
        "footer_settings": footer_settings,
        "current_language": current_language,
        "language_urls": language_urls,
        "canonical_url": language_urls.get(language_code, absolute_url),
    }
