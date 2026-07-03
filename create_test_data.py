#!/usr/bin/env python
"""
اسکریپت برای ایجاد داده‌های تست برای داشبورد
"""
import os
import django
from django.utils import timezone
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pouriabaghban3.settings')
django.setup()

from django.contrib.auth.models import User
from blog.models import BlogPost, BlogCategory, BlogAuthor, BlogComment
from contact.models import ContactMessage

print("📊 شروع ایجاد داده‌های تست...")

# بررسی وجود admin
try:
    admin_user = User.objects.get(username='admin')
    print(f"✅ کاربر admin یافت شد")
except User.DoesNotExist:
    print("❌ کاربر admin یافت نشد!")
    exit(1)

# بررسی BlogAuthor
try:
    blog_author = BlogAuthor.objects.get(user=admin_user)
except BlogAuthor.DoesNotExist:
    blog_author = BlogAuthor.objects.create(
        user=admin_user,
        bio="مدیر سایت",
        is_active=True
    )
    print(f"✅ BlogAuthor برای admin ایجاد شد")

# ایجاد دسته‌بندی
category, created = BlogCategory.objects.get_or_create(
    name="متفرقه",
    defaults={
        'slug': 'general',
        'description': 'پست‌های متفرقه',
        'color': '#007bff'
    }
)
print(f"{'✅ دسته‌بندی ایجاد شد' if created else '✅ دسته‌بندی موجود است'}")

# ایجاد 5 پست
posts_data = [
    {
        'title': 'اولین پست - Django مقدماتی',
        'excerpt': 'آموزش Django برای مبتدیان',
        'content': 'متن کامل مقاله درباره Django...' * 10
    },
    {
        'title': 'پست دوم - مدل‌های Django',
        'excerpt': 'درس داده‌بندی و مدل‌ها',
        'content': 'توضیح جزئی درباره ORM...' * 10
    },
    {
        'title': 'پست سوم - تمپلیت‌ها',
        'excerpt': 'کار با تمپلیت Django',
        'content': 'تمپلیت سیستم Django...' * 10
    },
    {
        'title': 'پست چهارم - Auth سیستم',
        'excerpt': 'احراز هویت کاربران',
        'content': 'سیستم احراز هویت built-in...' * 10
    },
    {
        'title': 'پست پنجم - API ساخت',
        'excerpt': 'ایجاد API با Django',
        'content': 'استفاده از Django REST Framework...' * 10
    },
]

published_count = 0
for i, post_data in enumerate(posts_data):
    post, created = BlogPost.objects.get_or_create(
        title=post_data['title'],
        defaults={
            'author': admin_user,
            'category': category,
            'excerpt': post_data['excerpt'],
            'content': post_data['content'],
            'status': 'published' if i < 3 else 'draft',
            'is_featured': i == 0,
            'views': (5 - i) * 10,
            'likes': (5 - i) * 2,
            'published_at': timezone.now() - timedelta(days=5-i) if i < 3 else None
        }
    )
    if created:
        print(f"✅ پست '{post_data['title']}' ایجاد شد")
        if post.status == 'published':
            published_count += 1
    else:
        print(f"⏭️  پست '{post_data['title']}' قبلاً موجود است")

# ایجاد 3 کامنت
post_published = BlogPost.objects.filter(status='published').first()
if post_published:
    comments_data = [
        {'author': 'احمد', 'email': 'ahmad@example.com', 'content': 'پست خوبی بود!', 'is_approved': True},
        {'author': 'فاطمه', 'email': 'fateme@example.com', 'content': 'مفید بود، متشکر', 'is_approved': True},
        {'author': 'علی', 'email': 'ali@example.com', 'content': 'بیشتر توضیح دهید', 'is_approved': False},
    ]
    
    for comment_data in comments_data:
        comment, created = BlogComment.objects.get_or_create(
            post=post_published,
            author=comment_data['author'],
            email=comment_data['email'],
            content=comment_data['content'],
            defaults={'is_approved': comment_data['is_approved']}
        )
        if created:
            print(f"✅ کامنت از {comment_data['author']} ایجاد شد")
        else:
            print(f"⏭️  کامنت از {comment_data['author']} قبلاً موجود است")

# ایجاد پیام‌های تماس
contacts_data = [
    {'name': 'مهدی', 'email': 'mehdi@example.com', 'subject': 'سؤال درباره خدمات', 'message': 'آیا می‌توانید بیشتر توضیح دهید؟', 'is_read': True, 'is_replied': False},
    {'name': 'نازنین', 'email': 'nazanin@example.com', 'subject': 'درخواست مشاوره', 'message': 'می‌خواهم برای پروژه مشاوره بگیرم', 'is_read': False, 'is_replied': False},
    {'name': 'رضا', 'email': 'reza@example.com', 'subject': 'بازخورد', 'message': 'سایت شما فوق‌العاده است!', 'is_read': True, 'is_replied': True},
]

for contact_data in contacts_data:
    contact, created = ContactMessage.objects.get_or_create(
        name=contact_data['name'],
        email=contact_data['email'],
        subject=contact_data['subject'],
        defaults={
            'message': contact_data['message'],
            'is_read': contact_data['is_read'],
            'is_replied': contact_data['is_replied'],
            'reply_message': 'پاسخ‌ها' if contact_data['is_replied'] else None,
            'replied_at': timezone.now() - timedelta(hours=2) if contact_data['is_replied'] else None
        }
    )
    if created:
        print(f"✅ پیام از {contact_data['name']} ایجاد شد")
    else:
        print(f"⏭️  پیام از {contact_data['name']} قبلاً موجود است")

print("\n" + "="*50)
print("✅ داده‌های تست با موفقیت ایجاد شدند!")
print(f"📊 آمار کلی:")
print(f"  - پست‌های منتشر شده: {BlogPost.objects.filter(status='published').count()}")
print(f"  - کل کامنت‌ها: {BlogComment.objects.count()}")
print(f"  - کل پیام‌های تماس: {ContactMessage.objects.count()}")
