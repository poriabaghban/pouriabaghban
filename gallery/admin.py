from django.contrib import admin

from .models import GalleryCategory, GalleryImage, PortfolioCategory, PortfolioItem


@admin.register(GalleryCategory)
class GalleryCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name", "description")


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "uploaded_by", "created_at", "is_featured")
    list_filter = ("category", "is_featured", "created_at", "uploaded_by")
    search_fields = ("title", "description")
    readonly_fields = ("created_at",)
    fieldsets = (
        ("اطلاعات اصلی", {"fields": ("title", "category", "image")}),
        ("جزئیات", {"fields": ("description", "uploaded_by", "is_featured")}),
        ("تاریخ", {"fields": ("created_at",), "classes": ("collapse",)}),
    )


@admin.register(PortfolioCategory)
class PortfolioCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name", "description")


@admin.register(PortfolioItem)
class PortfolioItemAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "uploaded_by", "created_at", "is_featured")
    list_filter = ("category", "is_featured", "created_at", "uploaded_by")
    search_fields = ("title", "description", "detail_description", "project_url")
    readonly_fields = ("created_at",)
    fieldsets = (
        ("اطلاعات اصلی", {"fields": ("title", "category", "image")}),
        ("جزئیات", {"fields": ("description", "detail_description", "detail_image", "project_file", "project_url", "uploaded_by", "is_featured")}),
        ("تاریخ", {"fields": ("created_at",), "classes": ("collapse",)}),
    )
