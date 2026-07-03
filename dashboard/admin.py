from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import UserRole


class UserRoleInline(admin.StackedInline):
    """نمایش نقش در صفحهٔ کاربر"""
    model = UserRole
    extra = 0
    fields = ('role', 'is_active', 'can_write', 'can_edit', 'can_delete', 'can_manage_comments', 'can_manage_users')
    readonly_fields = ()


class UserAdmin(BaseUserAdmin):
    """ادمین کاربران با نقش‌ها"""
    inlines = [UserRoleInline]
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_role', 'is_active', 'is_staff')
    list_filter = ('is_active', 'is_staff', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    
    def get_role(self, obj):
        """نمایش نقش کاربر"""
        try:
            role = obj.user_role
            return f"{role.get_role_display()}"
        except:
            return "بدون نقش"
    get_role.short_description = "🎭 نقش"


# پاک‌کردن ادمین پیش‌فرض و اضافه کردن ادمین سفارشی
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    """پنل مدیریت نقش‌های کاربری"""
    list_display = ('get_username', 'get_role_badge', 'is_active', 'can_write', 'can_manage_users')
    list_filter = ('role', 'is_active', 'created_at')
    search_fields = ('user__username', 'user__email', 'user__first_name')
    fieldsets = (
        ('👤 کاربر', {
            'fields': ('user',)
        }),
        ('🎭 نقش و وضعیت', {
            'fields': ('role', 'is_active')
        }),
        ('✅ اختیارات', {
            'fields': ('can_write', 'can_edit', 'can_delete', 'can_manage_comments', 'can_manage_users'),
            'description': 'اختیارات مربوطه بر اساس نقش خودکار تنظیم می‌شوند'
        }),
        ('📅 تاریخ', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')
    actions = ['make_active', 'make_inactive', 'make_admin', 'make_author', 'make_subscriber']
    
    def get_username(self, obj):
        return f"👤 {obj.user.username}"
    get_username.short_description = "کاربر"
    
    def get_role_badge(self, obj):
        roles = {
            'admin': '🔑 ادمین',
            'author': '✍️ نویسنده',
            'editor': '📝 ویرایشگر',
            'moderator': '🛡️ مدیریت‌کننده',
            'subscriber': '👤 مشترک',
        }
        return roles.get(obj.role, obj.role)
    get_role_badge.short_description = "🎭 نقش"
    
    def make_active(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} کاربر فعال شد.')
    make_active.short_description = '✅ فعال کردن انتخاب‌شدگان'
    
    def make_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} کاربر غیرفعال شد.')
    make_inactive.short_description = '❌ غیرفعال کردن انتخاب‌شدگان'
    
    def make_admin(self, request, queryset):
        for user_role in queryset:
            user_role.role = 'admin'
            user_role.save()
        self.message_user(request, f'{queryset.count()} کاربر به ادمین تبدیل شدند.')
    make_admin.short_description = '🔑 تبدیل به ادمین'
    
    def make_author(self, request, queryset):
        for user_role in queryset:
            user_role.role = 'author'
            user_role.save()
        self.message_user(request, f'{queryset.count()} کاربر به نویسنده تبدیل شدند.')
    make_author.short_description = '✍️ تبدیل به نویسنده'
    
    def make_subscriber(self, request, queryset):
        for user_role in queryset:
            user_role.role = 'subscriber'
            user_role.save()
        self.message_user(request, f'{queryset.count()} کاربر به مشترک تبدیل شدند.')
    make_subscriber.short_description = '👤 تبدیل به مشترک'
    
    def has_delete_permission(self, request, obj=None):
        """فقط ادمین می‌تواند حذف کند"""
        return request.user.is_superuser
