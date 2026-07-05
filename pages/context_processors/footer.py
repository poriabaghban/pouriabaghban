from pages.models import FooterSettings, SocialLink


def footer_context(request):
    footer = FooterSettings.objects.filter(is_active=True).first()
    social_links = SocialLink.objects.filter(is_active=True)

    return {
        "footer": footer,
        "social_links": social_links,
    }