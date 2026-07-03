# blog/admin.py
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

# اگر bilingual_admin رو ندارید، این خط رو کامنت کنید
# from bilingual_admin import LanguageFilterMixin, language_availability_filter
from .forms import BlogPostForm
from .models import BlogAuthor, BlogCategory, BlogComment, BlogPost, BlogPostDetailImage, BlogTag


admin.site.site_header = "Pouria Baghban Admin Panel"
admin.site.site_title = "Admin Panel"
admin.site.index_title = "داشبورد مدیریت"


@admin.register(BlogAuthor)
class BlogAuthorAdmin(admin.ModelAdmin):
    # تنظیم نام مدل برای نمایش در ادمین
    verbose_name = _("نویسنده")
    verbose_name_plural = _("نویسندگان")
    
    list_display = ("get_author_name", "get_email", "post_count", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("user__first_name", "user__last_name", "user__email", "user__username")
    readonly_fields = ("created_at",)
    fieldsets = (
        (_("اطلاعات کاربر"), {"fields": ("user", "is_active")}),
        (_("پروفایل"), {"fields": ("profile_image", "bio")}),
        (_("شبکه‌های اجتماعی"), {"fields": ("social_links",), "classes": ("collapse",)}),
    )

    def get_author_name(self, obj):
        name = f"{obj.user.first_name} {obj.user.last_name}".strip()
        return name or obj.user.username
    get_author_name.short_description = _("نام نویسنده")

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = _("ایمیل")
    
    def post_count(self, obj):
        return obj.user.blogpost_set.filter(status="published").count()
    post_count.short_description = _("تعداد پست‌ها")


@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    # تنظیم نام مدل برای نمایش در ادمین
    verbose_name = _("دسته‌بندی")
    verbose_name_plural = _("دسته‌بندی‌ها")
    
    list_display = ("name", "get_color_badge", "get_posts_count")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}

    def get_color_badge(self, obj):
        return format_html(
            '<span style="background-color: {}; padding: 5px 10px; border-radius: 3px; color: white;">{}</span>',
            obj.color,
            obj.color,
        )
    get_color_badge.short_description = _("رنگ")

    def get_posts_count(self, obj):
        count = obj.blogpost_set.filter(status="published").count()
        return format_html("<strong>{}</strong>", count)
    get_posts_count.short_description = _("تعداد پست‌ها")


@admin.register(BlogTag)
class BlogTagAdmin(admin.ModelAdmin):
    # تنظیم نام مدل برای نمایش در ادمین
    verbose_name = _("برچسب")
    verbose_name_plural = _("برچسب‌ها")
    
    list_display = ("name", "get_posts_count")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}

    def get_posts_count(self, obj):
        return obj.blogpost_set.filter(status="published").count()
    get_posts_count.short_description = _("تعداد پست‌ها")


class BlogPostDetailImageInline(admin.TabularInline):
    model = BlogPostDetailImage
    extra = 4
    fields = ("order", "image", "title", "content", "get_preview")
    readonly_fields = ("get_preview",)
    verbose_name = _("تصویر")
    verbose_name_plural = _("تصاویر")

    def get_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-width: 160px; height: auto;" />', obj.image.url)
        return _("No image uploaded.")
    get_preview.short_description = _("پیش‌نمایش")


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):  # LanguageFilterMixin رو بردار اگر ارور میده
    # تنظیم نام مدل برای نمایش در ادمین
    verbose_name = _("پست")
    verbose_name_plural = _("پست‌ها")
    
    form = BlogPostForm
    inlines = (BlogPostDetailImageInline,)
    list_display = ("get_admin_title", "author", "category", "get_status_badge", "get_active_badge", "get_homepage_badge", "views", "likes", "created_at")
    list_filter = ("status", "is_active", "is_on_homepage", "category", "created_at", "author", "is_featured")
    search_fields = ("title_fa", "content_fa", "excerpt_fa", "title_en", "content_en", "excerpt_en")
    readonly_fields = ("created_at", "updated_at", "views", "likes", "get_preview")
    filter_horizontal = ("tags",)
    actions = ["publish_posts", "draft_posts", "archive_posts", "activate_posts", "deactivate_posts", "feature_posts", "show_on_homepage", "hide_from_homepage"]
    fieldsets = (
        (_("اطلاعات اصلی"), {"fields": ("slug", "author", "category", "image", "get_preview")}),
        (_("محتوا فارسی"), {"fields": ("title_fa", "excerpt_fa", "content_fa")}),
        (_("محتوا انگلیسی"), {"fields": ("title_en", "excerpt_en", "content_en")}),
        (_("محتوا آلمانی"), {"fields": ("title_de", "excerpt_de", "content_de")}),
        (_("فایل‌های چندرسانه‌ای"), {"fields": ("audio_file", "audio_url", "video_file", "video_url")}),
        (_("فیلدهای قدیمی"), {"fields": ("title", "excerpt", "content"), "classes": ("collapse",)}),
        (_("تنظیمات انتشار"), {"fields": ("status", "published_at", "is_active", "is_featured", "is_on_homepage")}),
        (_("برچسب‌ها"), {"fields": ("tags",), "classes": ("collapse",)}),
        (_("آمار"), {"fields": ("views", "likes", "created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def get_admin_title(self, obj):
        return obj.title_fa or obj.title_en or obj.title
    get_admin_title.short_description = _("عنوان")

    def get_status_badge(self, obj):
        colors = {"draft": "#ffc107", "published": "#28a745", "archived": "#6c757d"}
        labels = {"draft": _("پیش‌نویس"), "published": _("منتشر شده"), "archived": _("بایگانی شده")}
        return format_html(
            '<span style="background-color: {}; padding: 5px 10px; border-radius: 3px; color: white;">{}</span>',
            colors.get(obj.status, "#007bff"),
            labels.get(obj.status, obj.status),
        )
    get_status_badge.short_description = _("وضعیت")

    def get_active_badge(self, obj):
        if obj.status == "published":
            return format_html('<span style="color: #155724; font-weight: 700;">✅ {}</span>', _("فعال"))
        return format_html('<span style="color: #856404; font-weight: 700;">⛔ {}</span>', _("غیرفعال"))
    get_active_badge.short_description = _("فعال")

    def get_homepage_badge(self, obj):
        if obj.is_on_homepage:
            return format_html('<span style="color: #155724; font-weight: 700;">✓ {}</span>', _("صفحه اصلی"))
        return format_html('<span style="color: #6c757d;">-</span>')
    get_homepage_badge.short_description = _("نمایش در صفحه اصلی")

    def get_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-width: 300px; height: auto;" />', obj.image.url)
        return _("تصویری آپلود نشده است.")
    get_preview.short_description = _("پیش‌نمایش تصویر")

    def publish_posts(self, request, queryset):
        updated = queryset.update(status="published")
        self.message_user(request, _("%(count)s پست منتشر شد.") % {"count": updated})
    publish_posts.short_description = _("انتشار پست‌های انتخاب شده")

    def draft_posts(self, request, queryset):
        updated = queryset.update(status="draft")
        self.message_user(request, _("%(count)s پست به پیش‌نویس منتقل شد.") % {"count": updated})
    draft_posts.short_description = _("انتقال به پیش‌نویس")

    def archive_posts(self, request, queryset):
        updated = queryset.update(status="archived")
        self.message_user(request, _("%(count)s پست بایگانی شد.") % {"count": updated})
    archive_posts.short_description = _("بایگانی پست‌ها")

    def activate_posts(self, request, queryset):
        updated = queryset.update(status="published")
        self.message_user(request, _("%(count)s پست فعال شد.") % {"count": updated})
    activate_posts.short_description = _("فعال کردن پست‌ها")

    def deactivate_posts(self, request, queryset):
        updated = queryset.update(status="draft")
        self.message_user(request, _("%(count)s پست غیرفعال شد.") % {"count": updated})
    deactivate_posts.short_description = _("غیرفعال کردن پست‌ها")

    def feature_posts(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, _("%(count)s پست ویژه شد.") % {"count": updated})
    feature_posts.short_description = _("ویژه کردن پست‌ها")

    def show_on_homepage(self, request, queryset):
        updated = queryset.update(is_on_homepage=True)
        self.message_user(request, _("%(count)s پست در صفحه اصلی نمایش داده می‌شود.") % {"count": updated})
    show_on_homepage.short_description = _("نمایش پست‌های انتخاب‌شده در صفحه اصلی")

    def hide_from_homepage(self, request, queryset):
        updated = queryset.update(is_on_homepage=False)
        self.message_user(request, _("%(count)s پست از صفحه اصلی برداشته شد.") % {"count": updated})
    hide_from_homepage.short_description = _("برداشتن پست‌های انتخاب‌شده از صفحه اصلی")

    def save_model(self, request, obj, form, change):
        if not change and not obj.author_id:
            obj.author = request.user
        super().save_model(request, obj, form, change)


@admin.register(BlogComment)
class BlogCommentAdmin(admin.ModelAdmin):
    # تنظیم نام مدل برای نمایش در ادمین
    verbose_name = _("نظر")
    verbose_name_plural = _("نظرات")
    
    list_display = ("author", "post", "get_parent_comment", "get_excerpt", "get_approval_status", "created_at")
    list_filter = ("is_approved", "created_at", "post")
    search_fields = ("author", "email", "content")
    readonly_fields = ("created_at", "get_full_comment")
    actions = ["approve_comments", "disapprove_comments"]
    fieldsets = (
        (_("اطلاعات فرستنده"), {"fields": ("author", "email", "post", "parent")}),
        (_("متن نظر"), {"fields": ("get_full_comment", "created_at")}),
        (_("وضعیت"), {"fields": ("is_approved",)}),
    )

    def get_excerpt(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    get_excerpt.short_description = _("خلاصه")

    def get_parent_comment(self, obj):
        return obj.parent.author if obj.parent_id else "-"
    get_parent_comment.short_description = _("پاسخ به")

    def get_approval_status(self, obj):
        if obj.is_approved:
            return format_html('<span style="color: green;">✅ {}</span>', _("تایید شده"))
        return format_html('<span style="color: red;">⏳ {}</span>', _("در انتظار تایید"))
    get_approval_status.short_description = _("وضعیت")

    def get_full_comment(self, obj):
        return format_html('<div style="white-space: pre-wrap; background: #f5f5f5; padding: 10px; border-radius: 5px;">{}</div>', obj.content)
    get_full_comment.short_description = _("متن کامل نظر")

    def approve_comments(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f"{updated} {_('نظر تایید شد.')}")
    approve_comments.short_description = _("تایید نظرات")

    def disapprove_comments(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f"{updated} {_('نظر رد شد.')}")
    disapprove_comments.short_description = _("رد کردن نظرات")
