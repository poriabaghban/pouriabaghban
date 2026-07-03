from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import get_language
from django.utils.translation import gettext_lazy as _
from django.utils.translation import gettext_lazy as _

class BlogAuthor(models.Model):
    """مدل برای مدیریت نویسندگان بلاگ"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="کاربر")
    bio = models.TextField(verbose_name="بیوگرافی", blank=True)
    profile_image = models.ImageField(upload_to='authors/', verbose_name="عکس پروفایل", blank=True, null=True)
    social_links = models.JSONField(default=dict, blank=True, verbose_name="لینک شبکه اجتماعی")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    
    class Meta:
        verbose_name = "نویسنده بلاگ"
        verbose_name_plural = "نویسندگان بلاگ"
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}" or self.user.username
    
    def post_count(self):
        # BlogPost doesn't have a DB field named `is_published` (it's a @property).
        # Filter by the stored `status` field instead.
        return self.user.blogpost_set.filter(status='published').count()


class BlogCategory(models.Model):
    """دسته بندی بلاگ"""
    name = models.CharField(max_length=100, verbose_name="نام دسته بندی  ")
    slug = models.SlugField(unique=True, verbose_name="نشانی", blank=True)
    description = models.TextField(blank=True, verbose_name="توضیح")
    color = models.CharField(max_length=7, default='#007bff', verbose_name="رنگ")
    
    class Meta:
        verbose_name = "دسته بندی بلاگ"
        verbose_name_plural = "دسته بندی های بلاگ"
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)


class BlogTag(models.Model):
    """برچسب های بلاگ """
    name = models.CharField(max_length=50, unique=True, verbose_name="نام برچسب")
    slug = models.SlugField(unique=True, blank=True)
    
    class Meta:
        verbose_name = " برچسب بلاگ "
        verbose_name_plural = "برچسب های بلاگ"
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)


class BlogPost(models.Model):
    """پست های بلاگ"""
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('published', _('Published')),
        ('archived', _('Archived')),
    ]
    
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('published', _('Published')),
        ('archived', _('Archived')),
    ]

    title_fa = models.CharField(max_length=200, blank=True, verbose_name="Title (Persian)")
    title_en = models.CharField(max_length=200, blank=True, verbose_name="Title (English)")
    title_de = models.CharField(max_length=200, blank=True, verbose_name="Title (German)")
    title = models.CharField(max_length=200, verbose_name="عنوان")
    slug = models.SlugField(unique=True, verbose_name="نشانی/لینک", blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="نویسنده", limit_choices_to={'blogauthor__is_active': True})
    category = models.ForeignKey(BlogCategory, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="دسته بندی")
    content_fa = models.TextField(blank=True, verbose_name="Content (Persian)")
    content_en = models.TextField(blank=True, verbose_name="Content (English)")
    content_de = models.TextField(blank=True, verbose_name="Content (German)")
    content = models.TextField(verbose_name="محتوا")
    excerpt_fa = models.TextField(max_length=500, blank=True, verbose_name="Excerpt (Persian)")
    excerpt_en = models.TextField(max_length=500, blank=True, verbose_name="Excerpt (English)")
    excerpt_de = models.TextField(max_length=500, blank=True, verbose_name="Excerpt (German)")
    excerpt = models.TextField(max_length=500, verbose_name="خلاصه")
    image = models.ImageField(upload_to='blog/', verbose_name="عکس", blank=True, null=True)
    audio_file = models.FileField(upload_to='blog/audio/', verbose_name=_("Audio file"), blank=True, null=True)
    audio_url = models.URLField(verbose_name=_("Audio URL"), blank=True)
    video_file = models.FileField(upload_to='blog/video/', verbose_name=_("Video file"), blank=True, null=True)
    video_url = models.URLField(verbose_name=_("Video URL"), blank=True)
    tags = models.ManyToManyField(BlogTag, verbose_name="برچسب ها", blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="وضعیت")
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    is_featured = models.BooleanField(default=False, verbose_name="برجسته")
    is_on_homepage = models.BooleanField(default=False, verbose_name="نمایش در صفحه اصلی")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی/ویرایش")
    published_at = models.DateTimeField(null=True, blank=True, verbose_name="تاریخ انتشار")
    views = models.IntegerField(default=0, verbose_name="تعداد بازدیدکنندگان")
    likes = models.IntegerField(default=0, verbose_name="تعداد لایک")
    
    class Meta:
        verbose_name = "پست بلاگ"
        verbose_name_plural = "پست های بلاگ"
        ordering = ['-published_at', '-created_at']
        permissions = [
            ("can_publish", "میتواند منتشر شود¯"),
            ("can_archive", "میتواند آرشیو شود"),
        ]
        default_permissions = ('add', 'change', 'delete', 'view')
    
    def __str__(self):
        return self.get_title() or self.title
    
    def save(self, *args, **kwargs):
        if not self.title_fa and self.title:
            self.title_fa = self.title
        if not self.content_fa and self.content:
            self.content_fa = self.content
        if not self.excerpt_fa and self.excerpt:
            self.excerpt_fa = self.excerpt
        if not self.title and self.title_fa:
            self.title = self.title_fa
        if not self.content and self.content_fa:
            self.content = self.content_fa
        if not self.excerpt and self.excerpt_fa:
            self.excerpt = self.excerpt_fa
        if not self.slug:
            self.slug = slugify(self.title_fa or self.title_en or self.title_de or self.title, allow_unicode=True)
        super().save(*args, **kwargs)
    
    @property
    def is_published(self):
        return self.status == 'published'

    def has_fa_content(self):
        return bool((self.title_fa or "").strip() and (self.content_fa or "").strip())

    def has_de_content(self):
        return bool((self.title_de or "").strip() and (self.content_de or "").strip())

    def has_en_content(self):
        return bool((self.title_en or "").strip() and (self.content_en or "").strip())

    def get_available_languages(self):
        languages = []
        if self.has_fa_content():
            languages.append("fa")
        if self.has_en_content():
            languages.append("en")
        if self.has_de_content():
            languages.append("de")
        return languages

    def is_available_in_language(self, language=None):
        language = (language or get_language() or "fa").split("-")[0]
        if language == "de":
            return self.has_de_content()
        if language == "en":
            return self.has_en_content()
        return self.has_fa_content()

    def get_title(self, language=None):
        language = (language or get_language() or "fa").split("-")[0]
        if language == "de":
            return self.title_de or self.title_fa or self.title
        if language == "en":
            return self.title_en or self.title_fa or self.title
        return self.title_fa or self.title

    def get_content(self, language=None):
        language = (language or get_language() or "fa").split("-")[0]
        if language == "de":
            return self.content_de or self.content_fa or self.content
        if language == "en":
            return self.content_en or self.content_fa or self.content
        return self.content_fa or self.content

    def get_excerpt(self, language=None):
        language = (language or get_language() or "fa").split("-")[0]
        if language == "de":
            return self.excerpt_de or self.excerpt_fa or self.excerpt
        if language == "en":
            return self.excerpt_en or self.excerpt_fa or self.excerpt
        return self.excerpt_fa or self.excerpt

    @property
    def read_time(self):
        """Estimate read time in minutes based on word count (approx 200 wpm)."""
        try:
            text = self.get_content() or ''
            words = len(text.split())
            minutes = max(1, (words + 199) // 200)
            return minutes
        except Exception:
            return 1


class BlogPostDetailImage(models.Model):
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name="detail_images", verbose_name="پست بلاگ")
    image = models.ImageField(upload_to="blog/details/", verbose_name="جزییات تصویر")
    title = models.CharField(max_length=200, blank=True, verbose_name="عنوان تصویر  ")
    content = models.TextField(blank=True, verbose_name=" متن تصویر  ")
    order = models.PositiveIntegerField(default=0, verbose_name="نویسنده")

    class Meta:
        verbose_name = "تصویر جزییات بلاگ"
        verbose_name_plural = "تصاویر جزییات بلاگ"
        ordering = ["order", "id"]

    def __str__(self):
        return self.title or f"Image {self.order} for {self.post.get_title()}"


class BlogComment(models.Model):
    """نظرات بلاگ"""
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='comments', verbose_name="پست")
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="replies",
        verbose_name="پاسخ به",
        blank=True,
        null=True,
    )
    author = models.CharField(max_length=100, verbose_name="نویسنده")
    email = models.EmailField(verbose_name="ایمیل")
    content = models.TextField(verbose_name=" متن نظر")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    is_approved = models.BooleanField(default=True, verbose_name="تایید شده")
    
    class Meta:
        verbose_name = " نظربلاگ"
        verbose_name_plural = "نظرات بلاگ"
        ordering = ['created_at']
    
    def __str__(self):
        return f"نظر توسط{self.author} در {self.post.title}"
