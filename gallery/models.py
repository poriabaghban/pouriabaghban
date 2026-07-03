from django.db import models
from django.contrib.auth.models import User

class GalleryCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name="نام دسته‌بندی")
    description = models.TextField(blank=True, verbose_name="توضیحات")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    
    class Meta:
        verbose_name = "دسته‌بندی گالری"
        verbose_name_plural = "دسته‌بندی های گالری"
    
    def __str__(self):
        return self.name


class GalleryImage(models.Model):
    title = models.CharField(max_length=200, verbose_name="عنوان")
    category = models.ForeignKey(GalleryCategory, on_delete=models.SET_NULL, null=True, verbose_name="دسته‌بندی")
    image = models.ImageField(upload_to='gallery/', verbose_name="تصویر")
    description = models.TextField(blank=True, verbose_name="توضیحات")
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="آپلود شده توسط")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    is_featured = models.BooleanField(default=False, verbose_name="برجسته")
    
    class Meta:
        verbose_name = "تصویر گالری"
        verbose_name_plural = "تصاویر گالری"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title



class PortfolioCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name="\u0646\u0627\u0645 \u062f\u0633\u062a\u0647\u200c\u0628\u0646\u062f\u06cc")
    description = models.TextField(blank=True, verbose_name="\u062a\u0648\u0636\u06cc\u062d\u0627\u062a")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="\u062a\u0627\u0631\u06cc\u062e \u0627\u06cc\u062c\u0627\u062f")

    class Meta:
        verbose_name = "\u062f\u0633\u062a\u0647\u200c\u0628\u0646\u062f\u06cc \u0646\u0645\u0648\u0646\u0647 \u06a9\u0627\u0631"
        verbose_name_plural = "\u062f\u0633\u062a\u0647\u200c\u0628\u0646\u062f\u06cc \u0647\u0627\u06cc \u0646\u0645\u0648\u0646\u0647 \u06a9\u0627\u0631"

    def __str__(self):
        return self.name


class PortfolioItem(models.Model):
    title = models.CharField(max_length=200, verbose_name="\u0639\u0646\u0648\u0627\u0646")
    category = models.ForeignKey(PortfolioCategory, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="\u062f\u0633\u062a\u0647\u200c\u0628\u0646\u062f\u06cc")
    image = models.ImageField(upload_to='portfolio/', verbose_name="\u062a\u0635\u0648\u06cc\u0631")
    description = models.TextField(blank=True, verbose_name="\u062a\u0648\u0636\u06cc\u062d\u0627\u062a")
    detail_description = models.TextField(blank=True, verbose_name="\u062c\u0632\u0626\u06cc\u0627\u062a \u06a9\u0627\u0645\u0644 \u0646\u0645\u0648\u0646\u0647 \u06a9\u0627\u0631")
    detail_image = models.ImageField(upload_to='portfolio/details/', blank=True, null=True, verbose_name="\u062a\u0635\u0648\u06cc\u0631 \u062c\u0632\u0626\u06cc\u0627\u062a")
    project_file = models.FileField(upload_to='portfolio/files/', blank=True, null=True, verbose_name="\u0641\u0627\u06cc\u0644 \u067e\u0631\u0648\u0698\u0647")
    project_url = models.URLField(blank=True, verbose_name="\u0644\u06cc\u0646\u06a9 \u067e\u0631\u0648\u0698\u0647")
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="\u0622\u067e\u0644\u0648\u062f \u0634\u062f\u0647 \u062a\u0648\u0633\u0637")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="\u062a\u0627\u0631\u06cc\u062e \u0627\u06cc\u062c\u0627\u062f")
    is_featured = models.BooleanField(default=False, verbose_name="\u0628\u0631\u062c\u0633\u062a\u0647")

    class Meta:
        verbose_name = "\u0646\u0645\u0648\u0646\u0647 \u06a9\u0627\u0631"
        verbose_name_plural = "\u0646\u0645\u0648\u0646\u0647 \u06a9\u0627\u0631\u0647\u0627"
        ordering = ['-created_at']

    def __str__(self):
        return self.title
