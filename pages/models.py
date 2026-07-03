from django.db import models
from django.utils.translation import get_language


def _lang(language=None):
    return (language or get_language() or "fa").split("-")[0]


def _pick(obj, base, language=None):
    language = _lang(language)
    if language == "de":
        return getattr(obj, f"{base}_de", "") or getattr(obj, f"{base}_fa", "") or getattr(obj, base, "")
    if language == "en":
        return getattr(obj, f"{base}_en", "") or getattr(obj, f"{base}_fa", "") or getattr(obj, base, "")
    return getattr(obj, f"{base}_fa", "") or getattr(obj, base, "")


def _has_lang(obj, language, *fields):
    language = _lang(language)
    suffix = language if language in ("en", "de") else "fa"
    return all(bool((getattr(obj, f"{field}_{suffix}", "") or "").strip()) for field in fields)

class PageSection(models.Model):
    """بخش‌های مختلف صفحات"""
    SECTION_CHOICES = [
        # سربرگ و فوتر
        ('hero', '1️⃣ قسمت بالای صفحه (Hero) - عنوان و تصویر بزرگ'),
        ('header', '2️⃣ سربرگ - منو و لوگو'),
        ('footer', '3️⃣ پایین صفحه - لینک‌ها و اطلاعات'),
        
        # درباره و معرفی
        ('about', '4️⃣ درباره ما - معرفی و بیوگرافی'),
        ('biography', '5️⃣ بیوگرافی تکمیلی - تاریخچه و پیشینه'),
        ('testimonials', '6️⃣ نظرات کلاینت‌ها - توصیه‌ها'),
        ('comments', 'نظرات کاربران صفحه اصلی'),
        
        # مهارت و تخصص
        ('skills', '7️⃣ مهارت‌ها - تکنولوژی‌ها و زبان‌های برنامه‌نویسی'),
        ('expertise', '8️⃣ تخصص‌ها - حوزه‌های کاری'),
        ('certifications', '9️⃣ گواهینامه‌ها - مدارک و دوره‌های اعتباری'),
        
        # خدمات و پروژه‌ها
        ('services', '🔟 خدمات - سرویس‌های ارائه شده'),
        ('service_details', '1️⃣1️⃣ جزئیات خدمات - توضیح کامل خدمات'),
        ('projects', '1️⃣2️⃣ پروژه‌های نمونه - کارهای انجام شده'),
        ('project_showcase', '1️⃣3️⃣ نمایش پروژه‌ها - پروژه‌های برجسته'),
        
        # تیم و تعاون
        ('team', '1️⃣4️⃣ تیم - اعضای تیم'),
        ('team_details', '1️⃣5️⃣ جزئیات تیم - معرفی اعضا'),
        ('partners', '1️⃣6️⃣ شریک‌ها - شریک‌های کسب‌وکاری'),
        
        # محصولات و نتایج
        ('portfolio', '1️⃣7️⃣ نمونه‌کارها - پورتفولیو'),
        ('achievements', '1️⃣8️⃣ دستاوردها - موفقیت‌ها و جوایز'),
        ('statistics', '1️⃣9️⃣ آمار و ارقام - نمودار و آمار'),
        
        # فرآیند کاری
        ('process', '2️⃣0️⃣ فرآیند کاری - مراحل انجام کار'),
        ('workflow', '2️⃣1️⃣ جریان کاری - نحوه همکاری'),
        ('timeline', '2️⃣2️⃣ جدول زمانی - مراحل و سر فاصل'),
        
        # تجربه و ارزش‌ها
        ('experience', '2️⃣3️⃣ تجربه - سابقه کاری'),
        ('values', '2️⃣4️⃣ ارزش‌های ما - اصول و باورها'),
        ('mission', '2️⃣5️⃣ ماموریت ما - هدف و راهبرد'),
        
        # درخواست و تماس
        ('cta', '2️⃣6️⃣ فراخوان عمل - دکمه‌های فراخوان'),
        ('contact_form', '2️⃣7️⃣ فرم تماس - فرم درخواست'),
        ('faq', '2️⃣8️⃣ پرسش‌های متداول - Q&A'),
        
        # محتویات اضافی
        ('blog_preview', '2️⃣9️⃣ پیش‌نمایش بلاگ - پست‌های اخیر'),
        ('gallery_preview', '3️⃣0️⃣ پیش‌نمایش گالری - تصاویر برجسته'),
    ]
    
    PAGE_CHOICES = [
        ('index', 'صفحه اصلی'),
        ('blog', 'بلاگ'),
        ('gallery', 'گالری'),
        ('contact', 'تماس با ما'),
        ('about', 'درباره ما'),
    ]
    
    page = models.CharField(max_length=20, choices=PAGE_CHOICES, verbose_name="صفحه")
    section = models.CharField(max_length=20, choices=SECTION_CHOICES, verbose_name="بخش")
    title_fa = models.CharField(max_length=200, blank=True, verbose_name="Title (Persian)")
    title_en = models.CharField(max_length=200, blank=True, verbose_name="Title (English)")
    title_de = models.CharField(max_length=200, blank=True, verbose_name="Title (German)")
    title = models.CharField(max_length=200, blank=True, verbose_name="عنوان")
    description_fa = models.TextField(blank=True, verbose_name="Description (Persian)")
    description_en = models.TextField(blank=True, verbose_name="Description (English)")
    description_de = models.TextField(blank=True, verbose_name="Description (German)")
    description = models.TextField(blank=True, verbose_name="توضیح")
    image = models.ImageField(upload_to='pages/', blank=True, null=True, verbose_name="تصویر")
    image2 = models.ImageField(upload_to='pages/', blank=True, null=True, verbose_name="تصویر دوم")
    image3 = models.ImageField(upload_to='pages/', blank=True, null=True, verbose_name="تصویر سوم")
    text_field_1_fa = models.TextField(blank=True, verbose_name="Text 1 (Persian)")
    text_field_1_en = models.TextField(blank=True, verbose_name="Text 1 (English)")
    text_field_1_de = models.TextField(blank=True, verbose_name="Text 1 (German)")
    text_field_1 = models.TextField(blank=True, verbose_name="متن 1")
    text_field_2 = models.TextField(blank=True, verbose_name="متن 2")
    text_field_3 = models.TextField(blank=True, verbose_name="متن 3")
    button_text_fa = models.CharField(max_length=100, blank=True, verbose_name="Button text (Persian)")
    button_text_en = models.CharField(max_length=100, blank=True, verbose_name="Button text (English)")
    button_text_de = models.CharField(max_length=100, blank=True, verbose_name="Button text (German)")
    button_text = models.CharField(max_length=100, blank=True, verbose_name="متن دکمه")
    button_url = models.URLField(blank=True, verbose_name="آدرس لینک دکمه")
    order = models.IntegerField(default=0, verbose_name="ترتیب نمایش")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ به‌روزرسانی")
    

    def has_fa_content(self):
        return _has_lang(self, "fa", "title", "description")

    def has_de_content(self):
        return _has_lang(self, "de", "title", "description")

    def has_en_content(self):
        return _has_lang(self, "en", "title", "description")

    def get_available_languages(self):
        return [lang for lang in ("fa", "en", "de") if self.is_available_in_language(lang)]

    def is_available_in_language(self, language=None):
        language = _lang(language)
        if language == "de":
            return self.has_de_content()
        if language == "en":
            return self.has_en_content()
        return self.has_fa_content()

    def get_title(self, language=None):
        return _pick(self, "title", language)

    def get_description(self, language=None):
        return _pick(self, "description", language)

    def get_text_field_1(self, language=None):
        return _pick(self, "text_field_1", language)

    def get_button_text(self, language=None):
        return _pick(self, "button_text", language)


    def save(self, *args, **kwargs):
        if not self.title_fa and self.title:
            self.title_fa = self.title
        if not self.description_fa and self.description:
            self.description_fa = self.description
        if not self.text_field_1_fa and self.text_field_1:
            self.text_field_1_fa = self.text_field_1
        if not self.button_text_fa and self.button_text:
            self.button_text_fa = self.button_text
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "بخش صفحه"
        verbose_name_plural = "بخش‌های صفحات"
        ordering = ['page', 'section', 'order']
        unique_together = ['page', 'section', 'order']
    
    def __str__(self):
        return f"{self.get_page_display()} - {self.get_section_display()}"


class PageContent(models.Model):
    """محتویات عمومی صفحات"""
    key = models.SlugField(unique=True, verbose_name="کلید")
    title_fa = models.CharField(max_length=200, blank=True, verbose_name="Page title (Persian)")
    title_en = models.CharField(max_length=200, blank=True, verbose_name="Page title (English)")
    title_de = models.CharField(max_length=200, blank=True, verbose_name="Page title (German)")
    title = models.CharField(max_length=200, verbose_name="عنوان")
    content_fa = models.TextField(blank=True, verbose_name="Page content (Persian)")
    content_en = models.TextField(blank=True, verbose_name="Page content (English)")
    content_de = models.TextField(blank=True, verbose_name="Page content (German)")
    content = models.TextField(verbose_name="محتوا")
    image = models.ImageField(upload_to='pages/', blank=True, null=True, verbose_name="تصویر")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ به‌روزرسانی")
    

    def has_fa_content(self):
        return _has_lang(self, "fa", "title", "content")

    def has_de_content(self):
        return _has_lang(self, "de", "title", "content")

    def has_en_content(self):
        return _has_lang(self, "en", "title", "content")

    def get_available_languages(self):
        return [lang for lang in ("fa", "en", "de") if self.is_available_in_language(lang)]

    def is_available_in_language(self, language=None):
        language = _lang(language)
        if language == "de":
            return self.has_de_content()
        if language == "en":
            return self.has_en_content()
        return self.has_fa_content()

    def get_title(self, language=None):
        return _pick(self, "title", language)

    def get_content(self, language=None):
        return _pick(self, "content", language)


    def save(self, *args, **kwargs):
        if not self.title_fa and self.title:
            self.title_fa = self.title
        if not self.content_fa and self.content:
            self.content_fa = self.content
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "محتوای صفحه"
        verbose_name_plural = "محتویات صفحات"
    
    def __str__(self):
        return self.title


class SiteSettings(models.Model):
    """تنظیمات عمومی سایت"""
    site_name = models.CharField(max_length=200, verbose_name="نام سایت")
    site_description = models.TextField(verbose_name="توضیح سایت")
    logo = models.ImageField(upload_to='pages/', verbose_name="لوگو")
    favicon = models.ImageField(upload_to='pages/', blank=True, null=True, verbose_name="آیکون")
    owner_name = models.CharField(max_length=100, verbose_name="نام مالک")
    owner_title = models.CharField(max_length=200, verbose_name="تخصص/شغل")
    owner_bio = models.TextField(verbose_name="بیوگرافی مالک")
    owner_image = models.ImageField(upload_to='pages/', verbose_name="عکس مالک")
    cv_file = models.FileField(upload_to='pages/', blank=True, null=True, verbose_name="رزومه (PDF)")
    email = models.EmailField(verbose_name="ایمیل")
    phone = models.CharField(max_length=20, verbose_name="شماره تماس")
    address = models.TextField(verbose_name="آدرس")
    
    class Meta:
        verbose_name = "تنظیمات سایت"
        verbose_name_plural = "تنظیمات سایت"
    
    def __str__(self):
        return self.site_name


class Skill(models.Model):
    """مهارت‌های صاحب سایت"""
    name = models.CharField(max_length=100, verbose_name="نام مهارت")
    percentage = models.IntegerField(default=50, verbose_name="درصد مهارت", help_text="0 تا 100")
    category = models.CharField(max_length=50, blank=True, verbose_name="دسته‌بندی")
    icon = models.CharField(max_length=100, blank=True, verbose_name="آیکن FontAwesome")
    order = models.IntegerField(default=0, verbose_name="ترتیب")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    
    class Meta:
        verbose_name = "مهارت"
        verbose_name_plural = "مهارت‌ها"
        ordering = ['order']
    
    def __str__(self):
        return self.name


class SocialLink(models.Model):
    """لینک‌های شبکه‌های اجتماعی"""
    PLATFORM_CHOICES = [
        ('twitter', 'توییتر'),
        ('facebook', 'فیس‌بوک'),
        ('instagram', 'اینستاگرام'),
        ('linkedin', 'لینکدین'),
        ('youtube', 'یوتیوب'),
        ('whatsapp', 'واتس‌اپ'),
        ('telegram', 'تلگرام'),
    ]
    
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES, verbose_name="پلتفرم")
    url = models.URLField(verbose_name="آدرس")
    icon = models.CharField(max_length=100, blank=True, verbose_name="آیکن FontAwesome")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    
    class Meta:
        verbose_name = "لینک شبکه اجتماعی"
        verbose_name_plural = "لینک‌های شبکه‌های اجتماعی"
        unique_together = ['platform']
    
    def __str__(self):
        return f"{self.get_platform_display()}"


class ErrorPage(models.Model):
    """صفحات خطا قابل تنظیم"""
    ERROR_CHOICES = [
        (400, 'خطای 400 - درخواست نامعتبر'),
        (403, 'خطای 403 - دسترسی ممنوع'),
        (404, 'خطای 404 - صفحه پیدا نشد'),
        (500, 'خطای 500 - خطای سرور'),
    ]
    
    status_code = models.IntegerField(unique=True, choices=ERROR_CHOICES, verbose_name="کد وضعیت")
    title = models.CharField(max_length=200, verbose_name="عنوان فارسی")
    description = models.TextField(verbose_name="توضیح فارسی")
    image = models.ImageField(upload_to='errors/', blank=True, null=True, verbose_name="تصویر خطا")
    button_text = models.CharField(max_length=100, default="بازگشت به صفحه اصلی", verbose_name="متن دکمه")
    button_url = models.CharField(max_length=200, default="/", verbose_name="آدرس دکمه")
    
    class Meta:
        verbose_name = "صفحه خطا"
        verbose_name_plural = "صفحات خطا"
    
    def __str__(self):
        return f"خطای {self.status_code}"


class Testimonial(models.Model):
    """نظرات و توصیه‌های کلاینت‌ها"""
    name = models.CharField(max_length=100, verbose_name="نام کلاینت")
    title = models.CharField(max_length=100, blank=True, verbose_name="عنوان/شرکت")
    message = models.TextField(verbose_name="پیام/نظر")
    rating = models.IntegerField(default=5, choices=[(i, f'{i} ستاره') for i in range(1, 6)], verbose_name="امتیاز")
    image = models.ImageField(upload_to='testimonials/', blank=True, null=True, verbose_name="عکس پروفایل")
    is_published = models.BooleanField(default=False, verbose_name="منتشر شده")
    order = models.IntegerField(default=0, verbose_name="ترتیب نمایش")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ به‌روزرسانی")
    
    class Meta:
        verbose_name = "نظر/توصیه"
        verbose_name_plural = "نظرات و توصیه‌ها"
        ordering = ['order', '-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.rating}⭐"

class NavbarItem(models.Model):
    """Extra items that can be added to the main navigation."""
    title_fa = models.CharField(max_length=80, blank=True, verbose_name="Title (Persian)")
    title_en = models.CharField(max_length=80, blank=True, verbose_name="Title (English)")
    title_de = models.CharField(max_length=80, blank=True, verbose_name="Title (German)")
    title = models.CharField(max_length=80, verbose_name="عنوان")
    url = models.CharField(
        max_length=300,
        verbose_name="آدرس لینک",
        help_text="مثال: /blog/ یا #about یا https://example.com",
    )
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش")
    opens_new_tab = models.BooleanField(default=False, verbose_name="باز شدن در تب جدید")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ به‌روزرسانی")


    def has_fa_content(self):
        return _has_lang(self, "fa", "title")

    def has_de_content(self):
        return _has_lang(self, "de", "title")

    def has_en_content(self):
        return _has_lang(self, "en", "title")

    def get_available_languages(self):
        return [lang for lang in ("fa", "en", "de") if self.is_available_in_language(lang)]

    def is_available_in_language(self, language=None):
        language = _lang(language)
        if language == "de":
            return self.has_de_content()
        if language == "en":
            return self.has_en_content()
        return self.has_fa_content()

    def get_title(self, language=None):
        return _pick(self, "title", language)


    def save(self, *args, **kwargs):
        if not self.title_fa and self.title:
            self.title_fa = self.title
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "آیتم نوبار"
        verbose_name_plural = "آیتم‌های نوبار"
        ordering = ["order", "title"]

    def __str__(self):
        return self.title


class FooterSettings(models.Model):
    """Editable footer content."""
    site_name = models.CharField(max_length=200, blank=True, verbose_name="Site name")
    logo = models.ImageField(upload_to="pages/footer/", blank=True, null=True, verbose_name="لوگوی فوتر")
    description_fa = models.TextField(blank=True, verbose_name="Footer description (Persian)")
    description_en = models.TextField(blank=True, verbose_name="Footer description (English)")
    description_de = models.TextField(blank=True, verbose_name="Footer description (German)")
    description = models.TextField(blank=True, verbose_name="متن معرفی فوتر")
    github_url = models.URLField(blank=True, verbose_name="Repository URL")
    instagram_url = models.URLField(blank=True, verbose_name="Instagram URL")
    telegram_url = models.URLField(blank=True, verbose_name="Telegram URL")
    email = models.EmailField(blank=True, verbose_name="ایمیل فوتر")
    phone = models.CharField(max_length=50, blank=True, verbose_name="Phone")
    copyright_text_fa = models.CharField(max_length=200, blank=True, verbose_name="Copyright text (Persian)")
    copyright_text_en = models.CharField(max_length=200, blank=True, verbose_name="Copyright text (English)")
    copyright_text_de = models.CharField(max_length=200, blank=True, verbose_name="Copyright text (German)")
    copyright_text = models.CharField(max_length=200, blank=True, verbose_name="متن کپی‌رایت")
    copyright_year = models.CharField(max_length=10, default="2024", verbose_name="سال کپی‌رایت")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ به‌روزرسانی")


    def has_fa_content(self):
        return bool((self.description_fa or self.copyright_text_fa or self.description or self.copyright_text or "").strip())

    def has_de_content(self):
        return bool((self.description_de or self.copyright_text_de or "").strip())

    def has_en_content(self):
        return bool((self.description_en or self.copyright_text_en or "").strip())

    def get_available_languages(self):
        return [lang for lang in ("fa", "en", "de") if self.is_available_in_language(lang)]

    def is_available_in_language(self, language=None):
        language = _lang(language)
        if language == "de":
            return self.has_de_content()
        if language == "en":
            return self.has_en_content()
        return self.has_fa_content()

    def get_description(self, language=None):
        return _pick(self, "description", language)

    def get_copyright_text(self, language=None):
        return _pick(self, "copyright_text", language)


    def save(self, *args, **kwargs):
        if not self.description_fa and self.description:
            self.description_fa = self.description
        if not self.copyright_text_fa and self.copyright_text:
            self.copyright_text_fa = self.copyright_text
        if self.is_active:
            FooterSettings.objects.exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "تنظیمات فوتر"
        verbose_name_plural = "تنظیمات فوتر"

    def __str__(self):
        return self.site_name or "تنظیمات فوتر"


class HomePageComment(models.Model):
    """User comments submitted from the home page."""
    name = models.CharField(max_length=100, verbose_name="نام")
    email = models.EmailField(verbose_name="ایمیل")
    comment = models.TextField(max_length=500, verbose_name="متن نظر")
    is_published = models.BooleanField(default=False, verbose_name="منتشر شود")
    is_read = models.BooleanField(default=False, verbose_name="خوانده شده")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ به‌روزرسانی")

    class Meta:
        verbose_name = "نظر کاربر صفحه اصلی"
        verbose_name_plural = "نظرات کاربران صفحه اصلی"
        ordering = ["order", "-created_at"]

    def __str__(self):
        return f"{self.name} - {self.created_at:%Y-%m-%d}"

