from pages.models import FooterSettings


def footer_context(request):
    try:
        footer = FooterSettings.objects.filter(is_active=True).first()
    except Exception:
        footer = None

    return {"footer": footer}
