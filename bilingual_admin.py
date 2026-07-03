from django.contrib import admin
from django.db.models import Q
from django.utils.html import format_html

LANGUAGE_FILTER_CHOICES = {
    "fa": {"label": "فارسی", "flag": ""},
    "en": {"label": "English", "flag": "🇬🇧"},
    "de": {"label": "Deutsch", "flag": "🇩🇪"},
    "all": {"label": "All / Alle / همه", "flag": "🌐"},
}


class LanguageAvailabilityFilter(admin.SimpleListFilter):
    title = "Available languages"
    parameter_name = "available_language"

    def lookups(self, request, model_admin):
        return (
            ("fa", "Persian"),
            ("de", "🇩🇪 German"),
            ("all_languages", "Persian 🇬🇧🇩🇪 All languages"),
        )

    def queryset(self, request, queryset):
        required = getattr(self, "language_required_fields", None) or ("title",)
        value = self.value()
        if not required or not value:
            return queryset
        fa_q = Q()
        en_q = Q()
        de_q = Q()
        for field in required:
            fa_q &= Q(**{f"{field}_fa__isnull": False}) & ~Q(**{f"{field}_fa": ""})
            en_q &= Q(**{f"{field}_en__isnull": False}) & ~Q(**{f"{field}_en": ""})
            de_q &= Q(**{f"{field}_de__isnull": False}) & ~Q(**{f"{field}_de": ""})
        if value == "fa":
            return queryset.filter(fa_q)
        if value == "en":
            return queryset.filter(en_q)
        if value == "de":
            return queryset.filter(de_q)
        if value == "all_languages":
            return queryset.filter(fa_q & en_q & de_q)
        return queryset


def language_availability_filter(required_fields):
    class ConfiguredLanguageAvailabilityFilter(LanguageAvailabilityFilter):
        language_required_fields = required_fields

    return ConfiguredLanguageAvailabilityFilter


class LanguageFilterMixin:
    change_list_template = "admin/language_change_list.html"
    change_form_template = "admin/language_change_form.html"
    language_required_fields = ("title",)
    language_search_fields = {
        "fa": (),
        "en": (),
        "de": (),
        "all": (),
    }

    def get_language_filter(self, request):
        lang = request.GET.get("lang") or request.session.get("admin_content_language") or "all"
        if lang not in LANGUAGE_FILTER_CHOICES:
            lang = "all"
        request.session["admin_content_language"] = lang
        return lang

    def _language_q(self, lang):
        query = Q()
        for field in self.language_required_fields:
            query &= Q(**{f"{field}_{lang}__isnull": False}) & ~Q(**{f"{field}_{lang}": ""})
        return query

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        lang = self.get_language_filter(request)
        if lang != "all":
            queryset = queryset.filter(self._language_q(lang))
        return queryset

    def get_search_results(self, request, queryset, search_term):
        lang = self.get_language_filter(request)
        if not search_term or lang == "all":
            return super().get_search_results(request, queryset, search_term)
        fields = self.language_search_fields.get(lang) or [f"{field}_{lang}" for field in self.language_required_fields]
        query = Q()
        for field in fields:
            query |= Q(**{f"{field}__icontains": search_term})
        return queryset.filter(query), False

    def available_languages(self, obj):
        flags = []
        if hasattr(obj, "has_fa_content") and obj.has_fa_content():
            flags.append("فارسی")
        if hasattr(obj, "has_en_content") and obj.has_en_content():
            flags.append("🇬🇧")
        if hasattr(obj, "has_de_content") and obj.has_de_content():
            flags.append("🇩🇪")
        return format_html('<span class="language-status">{}</span>', " ".join(flags) or "—")
    available_languages.short_description = "Available Languages"

    def get_language_context(self, request):
        current = self.get_language_filter(request)
        params = request.GET.copy()
        buttons = []
        for code, meta in LANGUAGE_FILTER_CHOICES.items():
            params["lang"] = code
            buttons.append({
                "code": code,
                "label": meta["label"],
                "flag": meta["flag"],
                "url": f"?{params.urlencode()}",
                "active": code == current,
            })
        return {"admin_content_language": current, "language_filter_buttons": buttons}

    def changelist_view(self, request, extra_context=None):
        extra_context = {**(extra_context or {}), **self.get_language_context(request)}
        return super().changelist_view(request, extra_context=extra_context)

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        extra_context = {**(extra_context or {}), **self.get_language_context(request)}
        return super().changeform_view(request, object_id=object_id, form_url=form_url, extra_context=extra_context)
