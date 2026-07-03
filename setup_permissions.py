import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pouriabaghban3.settings')
django.setup()

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from blog.models import BlogPost

# ایجاد گروه نویسندگان
authors_group, created = Group.objects.get_or_create(name='Blog Authors')

if created:
    print("✅ گروه 'Blog Authors' ایجاد شد")
else:
    print("ℹ️ گروه 'Blog Authors' قبلا موجود بود")

# دریافت content type برای BlogPost
blogpost_ct = ContentType.objects.get_for_model(BlogPost)

# دریافت permissions مورد نظر
permissions = Permission.objects.filter(
    content_type=blogpost_ct,
    codename__in=['add_blogpost', 'change_blogpost', 'delete_blogpost', 'can_publish', 'can_archive']
)

# اضافه کردن permissions به گروه
authors_group.permissions.set(permissions)
print(f"✅ {permissions.count()} Permission برای گروه اضافه شد")

# ایجاد گروه مدیران
admins_group, created = Group.objects.get_or_create(name='Blog Managers')
if created:
    print("✅ گروه 'Blog Managers' ایجاد شد")

# اضافه کردن تمام permissions به مدیران
all_permissions = Permission.objects.filter(content_type=blogpost_ct)
admins_group.permissions.set(all_permissions)
print(f"✅ تمام Permissions برای مدیران اضافه شد")

print("\n🎉 سیستم Permissions موفقانه راه‌اندازی شد!")
print("\n📋 مراحل استفاده:")
print("1. به Admin > Users بروید")
print("2. یک کاربر جدید ایجاد کنید")
print("3. آن کاربر را به گروه 'Blog Authors' اضافه کنید")
print("4. اکنون آن کاربر می‌تواند پست‌ها بسازد اما نه منتشر کند")
print("5. مدیر می‌تواند پست‌ها را منتشر/آرشیو کند")
