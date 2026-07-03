from django.contrib import admin
from django.utils.html import format_html, format_html_join

from bilingual_admin import LanguageFilterMixin, language_availability_filter
from .models import ErrorPage, FooterSettings, HomePageComment, NavbarItem, PageContent, PageSection, SiteSettings, Skill, SocialLink, Testimonial

PROGRAMMING_ICON_CHOICES = (
    ("HTML5 logo", "fa-brands fa-html5", "assets/fonts/fontawesome-free-7.0.0-web/svgs/brands/html5.svg"),
    ("CSS3 logo", "fa-brands fa-css3-alt", "assets/fonts/fontawesome-free-7.0.0-web/svgs/brands/css3-alt.svg"),
    ("JavaScript logo", "fa-brands fa-js", "assets/fonts/fontawesome-free-7.0.0-web/svgs/brands/js.svg"),
    ("React logo", "fa-brands fa-react", "assets/fonts/fontawesome-free-7.0.0-web/svgs/brands/react.svg"),
    ("Python logo", "fa-brands fa-python", "assets/fonts/fontawesome-free-7.0.0-web/svgs/brands/python.svg"),
    ("Git logo", "fa-brands fa-git-alt", "assets/fonts/fontawesome-free-7.0.0-web/svgs/brands/git-alt.svg"),
    ("Docker logo", "fa-brands fa-docker", "assets/fonts/fontawesome-free-7.0.0-web/svgs/brands/docker.svg"),
    ("Bootstrap logo", "fa-brands fa-bootstrap", "assets/fonts/fontawesome-free-7.0.0-web/svgs/brands/bootstrap.svg"),
    ("Node.js logo", "fa-brands fa-node-js", "assets/fonts/fontawesome-free-7.0.0-web/svgs/brands/node-js.svg"),
    ("Vue.js logo", "fa-brands fa-vuejs", "assets/fonts/fontawesome-free-7.0.0-web/svgs/brands/vuejs.svg"),
    ("Angular logo", "fa-brands fa-angular", "assets/fonts/fontawesome-free-7.0.0-web/svgs/brands/angular.svg"),
    ("Laravel logo", "fa-brands fa-laravel", "assets/fonts/fontawesome-free-7.0.0-web/svgs/brands/laravel.svg"),
    ("PHP logo", "fa-brands fa-php", "assets/fonts/fontawesome-free-7.0.0-web/svgs/brands/php.svg"),
    ("WordPress logo", "fa-brands fa-wordpress", "assets/fonts/fontawesome-free-7.0.0-web/svgs/brands/wordpress.svg"),
    ("Sass logo", "fa-brands fa-sass", "assets/fonts/fontawesome-free-7.0.0-web/svgs/brands/sass.svg"),
    ("NPM logo", "fa-brands fa-npm", "assets/fonts/fontawesome-free-7.0.0-web/svgs/brands/npm.svg"),
    ("Yarn logo", "fa-brands fa-yarn", "assets/fonts/fontawesome-free-7.0.0-web/svgs/brands/yarn.svg"),
    ("Gitlab logo", "fa-brands fa-gitlab", "assets/fonts/fontawesome-free-7.0.0-web/svgs/brands/gitlab.svg"),
    ("Database icon", "fa-solid fa-database", "assets/fonts/fontawesome-free-7.0.0-web/svgs/solid/database.svg"),
    ("Code icon", "fa-solid fa-code", "assets/fonts/fontawesome-free-7.0.0-web/svgs/solid/code.svg"),
    ("Terminal icon", "fa-solid fa-terminal", "assets/fonts/fontawesome-free-7.0.0-web/svgs/solid/terminal.svg"),
    ("Laptop code icon", "fa-solid fa-laptop-code", "assets/fonts/fontawesome-free-7.0.0-web/svgs/solid/laptop-code.svg"),
    ("Bug icon", "fa-solid fa-bug", "assets/fonts/fontawesome-free-7.0.0-web/svgs/solid/bug.svg"),
    ("Server icon", "fa-solid fa-server", "assets/fonts/fontawesome-free-7.0.0-web/svgs/solid/server.svg"),
)


@admin.register(PageSection)
class PageSectionAdmin(LanguageFilterMixin, admin.ModelAdmin):
    list_display = ("get_admin_title", "page", "section", "available_languages", "order", "is_active")
    list_filter = (language_availability_filter(("title", "description")), "page", "section", "is_active")
    search_fields = ("title_fa", "description_fa", "title_en", "description_en", "title_de", "description_de", "title", "description")
    language_required_fields = ("title", "description")
    language_search_fields = {
        "fa": ("title_fa", "description_fa", "text_field_1_fa", "button_text_fa"),
        "en": ("title_en", "description_en", "text_field_1_en", "button_text_en"),
        "de": ("title_de", "description_de", "text_field_1_de", "button_text_de"),
        "all": ("title_fa", "description_fa", "title_en", "description_en", "title_de", "description_de", "title", "description"),
    }
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("Main information", {"fields": ("page", "section", "order", "is_active")} ),
        ("Persian content", {"fields": ("title_fa", "description_fa", "text_field_1_fa", "button_text_fa"), "classes": ("lang-fa-section",)}),
        ("English content", {"fields": ("title_en", "description_en", "text_field_1_en", "button_text_en"), "classes": ("lang-en-section",)}),
        ("German content", {"fields": ("title_de", "description_de", "text_field_1_de", "button_text_de"), "classes": ("lang-de-section",)}),
        ("Legacy Persian fields", {"fields": ("title", "description", "text_field_1", "text_field_2", "text_field_3", "button_text"), "classes": ("collapse",)}),
        ("Images", {"fields": ("image", "image2", "image3")} ),
        ("Button", {"fields": ("button_url",), "classes": ("collapse",)}),
        ("Dates", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def get_admin_title(self, obj):
        return obj.get_title()
    get_admin_title.short_description = "Title"


@admin.register(PageContent)
class PageContentAdmin(LanguageFilterMixin, admin.ModelAdmin):
    list_display = ("get_admin_title", "key", "available_languages", "is_active")
    list_filter = (language_availability_filter(("title", "content")), "is_active", "created_at")
    search_fields = ("title_fa", "content_fa", "title_en", "content_en", "title_de", "content_de", "title", "content")
    language_required_fields = ("title", "content")
    language_search_fields = {
        "fa": ("title_fa", "content_fa"),
        "en": ("title_en", "content_en"),
        "de": ("title_de", "content_de"),
        "all": ("title_fa", "content_fa", "title_en", "content_en", "title_de", "content_de", "title", "content"),
    }
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("Main information", {"fields": ("key", "is_active", "image")} ),
        ("Persian content", {"fields": ("title_fa", "content_fa"), "classes": ("lang-fa-section",)}),
        ("English content", {"fields": ("title_en", "content_en"), "classes": ("lang-en-section",)}),
        ("German content", {"fields": ("title_de", "content_de"), "classes": ("lang-de-section",)}),
        ("Legacy Persian fields", {"fields": ("title", "content"), "classes": ("collapse",)}),
        ("Dates", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def get_admin_title(self, obj):
        return obj.get_title()
    get_admin_title.short_description = "Title"


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ("site_name", "owner_name")
    fieldsets = (
        ("اطلاعات سایت", {"fields": ("site_name", "site_description", "logo", "favicon")}),
        ("اطلاعات مالک", {"fields": ("owner_name", "owner_title", "owner_bio", "owner_image", "cv_file")}),
        ("اطلاعات تماس", {"fields": ("email", "phone", "address")}),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("name", "percentage", "category", "is_active", "order")
    list_filter = ("category", "percentage", "is_active")
    list_editable = ("percentage", "is_active", "order")
    search_fields = ("name", "category", "icon")
    ordering = ("order",)
    readonly_fields = ("get_percentage_display", "skill_icon_guide", "icon_preview")
    fieldsets = (
        ("Skill information", {"fields": ("name", "category", "order", "is_active")}),
        ("Skill percentage", {"fields": ("percentage", "get_percentage_display"), "description": "Enter a number from 0 to 100."}),
        (
            "Logo / icon",
            {
                "fields": ("skill_icon_guide", "icon", "icon_preview"),
                "description": "Search in English, copy the ready Font Awesome class, then paste it in the icon field. Example search: LOGO HTML",
            },
        ),
    )

    def get_percentage_display(self, obj):
        filled = int(obj.percentage / 5)
        empty = 20 - filled
        bar = "#" * filled + "-" * empty
        return f"{bar} {obj.percentage}%"
    get_percentage_display.short_description = "Skill percentage"

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name == "icon":
            formfield.help_text = (
                "Type/paste a Font Awesome class. Examples: "
                "fa-brands fa-html5, fa-brands fa-python, fa-solid fa-code."
            )
        return formfield

    def skill_icon_guide(self, obj=None):
        rows = format_html_join(
            "",
            (
                '<tr class="skill-icon-row" data-search="{} {} {}">'
                '<td style="padding: 6px; border-bottom: 1px solid #eee;"><strong>{}</strong></td>'
                '<td style="padding: 6px; border-bottom: 1px solid #eee;"><code>{}</code></td>'
                '<td style="padding: 6px; border-bottom: 1px solid #eee;"><code>{}</code></td>'
                "</tr>"
            ),
            (
                (
                    label.lower(),
                    icon_class.lower(),
                    svg_path.lower(),
                    label,
                    icon_class,
                    svg_path,
                )
                for label, icon_class, svg_path in PROGRAMMING_ICON_CHOICES
            ),
        )
        return format_html(
            """
            <div class="skill-icon-guide" style="max-width: 980px;">
              <p style="margin: 0 0 10px;">
                Search ready programming SVG/logo names in English. For HTML, search
                <code>LOGO HTML</code> or <code>HTML5 logo</code>, then copy the class.
              </p>
              <input id="skill-icon-search" type="search" placeholder="Search: LOGO HTML, Python, React, database..."
                     style="box-sizing: border-box; width: 100%; max-width: 520px; padding: 8px 10px; margin-bottom: 12px;">
              <table id="skill-icon-table" style="width: 100%; border-collapse: collapse;">
                <thead>
                  <tr>
                    <th style="text-align: left; padding: 6px; border-bottom: 1px solid #ddd;">English search name</th>
                    <th style="text-align: left; padding: 6px; border-bottom: 1px solid #ddd;">Paste this in icon field</th>
                    <th style="text-align: left; padding: 6px; border-bottom: 1px solid #ddd;">Local SVG file</th>
                  </tr>
                </thead>
                <tbody>{}</tbody>
              </table>
            </div>
            <script>
              (function() {{
                var input = document.getElementById("skill-icon-search");
                var rows = document.querySelectorAll("#skill-icon-table .skill-icon-row");
                if (!input || !rows.length) return;
                input.addEventListener("input", function() {{
                  var value = input.value.toLowerCase().trim();
                  rows.forEach(function(row) {{
                    row.style.display = row.dataset.search.indexOf(value) === -1 ? "none" : "";
                  }});
                }});
              }})();
            </script>
            """,
            rows,
        )
    skill_icon_guide.short_description = "Programming logo guide"

    def icon_preview(self, obj):
        if not obj or not obj.icon:
            return "No icon selected yet."
        return format_html(
            '<span style="display: inline-flex; align-items: center; gap: 10px;">'
            '<i class="{}" style="font-size: 28px;"></i>'
            "<code>{}</code>"
            "</span>",
            obj.icon,
            obj.icon,
        )
    icon_preview.short_description = "Current icon preview"
@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
    list_display = ("platform", "is_active")
    list_filter = ("is_active", "platform")
    fieldsets = (("اطلاعات", {"fields": ("platform", "url", "icon", "is_active")}),)


@admin.register(ErrorPage)
class ErrorPageAdmin(admin.ModelAdmin):
    list_display = ("get_status_code", "title")
    fieldsets = (
        ("اطلاعات خطا", {"fields": ("status_code", "title", "description", "image")}),
        ("دکمه", {"fields": ("button_text", "button_url")}),
    )

    def get_status_code(self, obj):
        return obj.status_code
    get_status_code.short_description = "کد وضعیت"


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ("name", "title", "get_rating_stars", "is_published", "order")
    list_filter = ("is_published", "rating", "created_at")
    list_editable = ("order", "is_published")
    search_fields = ("name", "title", "message")
    ordering = ("order", "-created_at")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("اطلاعات کلاینت", {"fields": ("name", "title", "image")}),
        ("نظر و امتیاز", {"fields": ("message", "rating", "order")}),
        ("وضعیت انتشار", {"fields": ("is_published",)}),
        ("تاریخ", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def get_rating_stars(self, obj):
        return "★" * obj.rating
    get_rating_stars.short_description = "امتیاز"


@admin.register(NavbarItem)
class NavbarItemAdmin(LanguageFilterMixin, admin.ModelAdmin):
    list_display = ("get_admin_title", "available_languages", "url", "order", "opens_new_tab", "is_active")
    list_filter = (language_availability_filter(("title",)), "is_active", "opens_new_tab")
    list_editable = ("order", "is_active")
    search_fields = ("title_fa", "title_en", "title_de", "title", "url")
    language_required_fields = ("title",)
    language_search_fields = {
        "fa": ("title_fa",),
        "en": ("title_en",),
        "de": ("title_de",),
        "all": ("title_fa", "title_en", "title_de", "title"),
    }
    ordering = ("order", "title")
    fieldsets = (
        ("Main link settings", {"fields": ("url", "order")} ),
        ("Persian content", {"fields": ("title_fa",), "classes": ("lang-fa-section",)}),
        ("English content", {"fields": ("title_en",), "classes": ("lang-en-section",)}),
        ("German content", {"fields": ("title_de",), "classes": ("lang-de-section",)}),
        ("Legacy Persian fields", {"fields": ("title",), "classes": ("collapse",)}),
        ("Display behavior", {"fields": ("opens_new_tab", "is_active")} ),
    )

    def get_admin_title(self, obj):
        return obj.get_title()
    get_admin_title.short_description = "Title"


@admin.register(FooterSettings)
class FooterSettingsAdmin(LanguageFilterMixin, admin.ModelAdmin):
    list_display = ("site_name", "email", "phone", "available_languages", "get_admin_copyright", "is_active")
    list_editable = ("is_active",)
    language_required_fields = ("description", "copyright_text")
    search_fields = ("site_name", "description_fa", "description_en", "description_de", "copyright_text_fa", "copyright_text_en", "copyright_text_de", "description", "copyright_text", "email", "phone")
    fieldsets = (
        ("Main footer settings", {"fields": ("site_name", "logo", "email", "phone", "github_url", "instagram_url", "telegram_url", "copyright_year", "is_active")} ),
        ("Persian content", {"fields": ("description_fa", "copyright_text_fa"), "classes": ("lang-fa-section",)}),
        ("English content", {"fields": ("description_en", "copyright_text_en"), "classes": ("lang-en-section",)}),
        ("German content", {"fields": ("description_de", "copyright_text_de"), "classes": ("lang-de-section",)}),
        ("Legacy Persian fields", {"fields": ("description", "copyright_text"), "classes": ("collapse",)}),
    )

    def get_admin_copyright(self, obj):
        return obj.get_copyright_text()
    get_admin_copyright.short_description = "Copyright"

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(HomePageComment)
class HomePageCommentAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "created_at", "is_published", "is_read", "order")
    list_filter = ("is_published", "is_read", "created_at")
    list_editable = ("is_published", "is_read", "order")
    search_fields = ("name", "email", "comment")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("order", "-created_at")
    actions = ("publish_comments", "unpublish_comments", "mark_as_read")
    fieldsets = (
        ("اطلاعات کاربر", {"fields": ("name", "email")}),
        ("نظر", {"fields": ("comment", "order")}),
        ("وضعیت", {"fields": ("is_published", "is_read")}),
        ("تاریخ", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def publish_comments(self, request, queryset):
        updated = queryset.update(is_published=True, is_read=True)
        self.message_user(request, f"{updated} نظر منتشر شد.")
    publish_comments.short_description = "انتشار نظرات انتخاب‌شده"

    def unpublish_comments(self, request, queryset):
        updated = queryset.update(is_published=False)
        self.message_user(request, f"{updated} نظر از انتشار خارج شد.")
    unpublish_comments.short_description = "خارج کردن از انتشار"

    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f"{updated} نظر خوانده شد.")
    mark_as_read.short_description = "علامت‌گذاری به عنوان خوانده‌شده"
