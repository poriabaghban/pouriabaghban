from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from django.views.decorators.http import require_http_methods

from blog.models import BlogPost, BlogComment, BlogAuthor
from contact.models import ContactMessage
from pages.models import PageSection, Skill
from .models import UserRole
from .decorators import admin_required, staff_only, superuser_only


def is_staff(user):
    return user.is_staff


def can_manage_users(user):
    """بررسی اینکه آیا کاربر می‌تواند کاربران را مدیریت کند"""
    try:
        return user.user_role.can_manage_users or user.is_superuser
    except:
        return user.is_superuser


@admin_required
def dashboard(request):
    """داشبورد آماری اصلی"""
    
    # آمار کلی
    total_posts = BlogPost.objects.count()
    published_posts = BlogPost.objects.filter(status='published').count()
    draft_posts = BlogPost.objects.filter(status='draft').count()
    archived_posts = BlogPost.objects.filter(status='archived').count()
    
    # کامنت‌ها
    total_comments = BlogComment.objects.count()
    approved_comments = BlogComment.objects.filter(is_approved=True).count()
    pending_comments = BlogComment.objects.filter(is_approved=False).count()
    
    # پیام‌های تماس
    total_messages = ContactMessage.objects.count()
    unread_messages = ContactMessage.objects.filter(is_read=False).count()
    unanswered_messages = ContactMessage.objects.filter(is_replied=False).count()
    
    # نویسندگان
    total_authors = BlogAuthor.objects.filter(is_active=True).count()
    
    # آخرین پست‌ها
    recent_posts = BlogPost.objects.select_related('author').order_by('-published_at', '-created_at')[:5]
    
    # آخرین کامنت‌های منتظر تایید
    pending_comments_list = BlogComment.objects.filter(is_approved=False).select_related('post').order_by('-created_at')[:5]
    
    # آمار امروز
    today = timezone.now().date()
    today_posts = BlogPost.objects.filter(published_at__date=today).count()
    today_comments = BlogComment.objects.filter(created_at__date=today).count()
    
    # آمار این هفته
    week_ago = timezone.now() - timedelta(days=7)
    week_posts = BlogPost.objects.filter(published_at__gte=week_ago).count()
    week_comments = BlogComment.objects.filter(created_at__gte=week_ago).count()
    
    # محبوب‌ترین پست‌ها
    popular_posts = BlogPost.objects.filter(status='published').order_by('-published_at')[:5]
    
    # نویسندگان برتر
    top_authors = BlogAuthor.objects.annotate(
        post_count=Count('user__blogpost', filter=Q(user__blogpost__status='published'))
    ).order_by('-post_count')[:5]
    
    context = {
        # آمار کلی
        'total_posts': total_posts,
        'published_posts': published_posts,
        'draft_posts': draft_posts,
        'archived_posts': archived_posts,
        
        # کامنت‌ها
        'total_comments': total_comments,
        'approved_comments': approved_comments,
        'pending_comments': pending_comments,
        
        # نویسندگان
        'total_authors': total_authors,
        
        # لیست‌های اخیر
        'recent_posts': recent_posts,
        'pending_comments_list': pending_comments_list,
        
        # آمار امروز
        'today_posts': today_posts,
        'today_comments': today_comments,
        
        # آمار هفتگی
        'week_posts': week_posts,
        'week_comments': week_comments,
        
        # محبوب‌ترین
        'popular_posts': popular_posts,
        'top_authors': top_authors,
    }
    
    return render(request, 'dashboard/dashboard.html', context)


@admin_required
def dashboard_api(request):
    """API برای داشبورد (JSON) - واقعی وصل شده به دیتابیس"""
    from django.http import JsonResponse
    
    # آمار کلی پست‌ها
    total_posts = BlogPost.objects.count()
    published_posts = BlogPost.objects.filter(status='published').count()
    draft_posts = BlogPost.objects.filter(status='draft').count()
    archived_posts = BlogPost.objects.filter(status='archived').count()
    
    # آمار نظرات
    total_comments = BlogComment.objects.count()
    approved_comments = BlogComment.objects.filter(is_approved=True).count()
    pending_comments = BlogComment.objects.filter(is_approved=False).count()
    
    # آمار امروز
    today = timezone.now().date()
    today_posts = BlogPost.objects.filter(published_at__date=today).count()
    today_comments = BlogComment.objects.filter(created_at__date=today).count()
    
    # آمار این ماه
    month_ago = timezone.now() - timedelta(days=30)
    month_posts = BlogPost.objects.filter(published_at__gte=month_ago).count()
    month_comments = BlogComment.objects.filter(created_at__gte=month_ago).count()
    
    # تعداد کاربران
    from django.contrib.auth.models import User
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    staff_users = User.objects.filter(is_staff=True).count()
    
    # تعداد بازدید واقعی
    total_views = sum(post.views for post in BlogPost.objects.all())
    
    data = {
        'timestamp': timezone.now().isoformat(),
        'posts': {
            'total': total_posts,
            'published': published_posts,
            'draft': draft_posts,
            'archived': archived_posts,
            'today': today_posts,
            'month': month_posts,
            'views': total_views,
        },
        'comments': {
            'total': total_comments,
            'approved': approved_comments,
            'pending': pending_comments,
            'today': today_comments,
            'month': month_comments,
        },
        'users': {
            'total': total_users,
            'active': active_users,
            'staff': staff_users,
        },
    }
    return JsonResponse(data)


@admin_required
def admin_dashboard_home(request):
    """صفحه اصلی پنل مدیریت"""
    
    # آمار کلی
    total_posts = BlogPost.objects.count()
    published_posts = BlogPost.objects.filter(status='published').count()
    total_comments = BlogComment.objects.count()
    pending_comments = BlogComment.objects.filter(is_approved=False).count()
    total_messages = ContactMessage.objects.count()
    unread_messages = ContactMessage.objects.filter(is_read=False).count()
    total_authors = BlogAuthor.objects.filter(is_active=True).count()
    
    # لیست‌های اخیر
    recent_posts = BlogPost.objects.select_related('author').order_by('-published_at', '-created_at')[:5]
    pending_comments_list = BlogComment.objects.filter(is_approved=False).select_related('post').order_by('-created_at')[:5]
    unread_messages_list = ContactMessage.objects.filter(is_read=False).order_by('-created_at')[:5]
    
    context = {
        'total_posts': total_posts,
        'published_posts': published_posts,
        'total_comments': total_comments,
        'pending_comments': pending_comments,
        'total_messages': total_messages,
        'unread_messages': unread_messages,
        'total_authors': total_authors,
        'recent_posts': recent_posts,
        'pending_comments_list': pending_comments_list,
        'unread_messages_list': unread_messages_list,
    }
    
    return render(request, 'admin_dashboard.html', context)


@admin_required
def manage_users(request):
    """مدیریت کاربران و نقش‌های آن‌ها"""
    users = User.objects.all().select_related('user_role')
    
    # فیلترکردن
    role_filter = request.GET.get('role')
    status_filter = request.GET.get('status')
    
    if role_filter:
        users = users.filter(user_role__role=role_filter)
    
    if status_filter == 'active':
        users = users.filter(is_active=True)
    elif status_filter == 'inactive':
        users = users.filter(is_active=False)
    
    context = {
        'users': users,
        'role_filter': role_filter,
        'status_filter': status_filter,
        'role_choices': UserRole.ROLE_CHOICES,
    }
    
    return render(request, 'dashboard/manage_users.html', context)


@admin_required
@require_http_methods(["GET", "POST"])
def edit_user_role(request, user_id):
    """ویرایش نقش کاربر"""
    user = get_object_or_404(User, pk=user_id)
    user_role, created = UserRole.objects.get_or_create(user=user)
    
    if request.method == 'POST':
        role = request.POST.get('role')
        is_active = request.POST.get('is_active') == 'on'
        
        if role in dict(UserRole.ROLE_CHOICES):
            user_role.role = role
            user_role.is_active = is_active
            user_role.save()
            
            messages.success(request, f'✅ نقش کاربر {user.username} به {user_role.get_role_display()} تغییر یافت.')
            return redirect('dashboard:manage-users')
        else:
            messages.error(request, '❌ نقش نامعتبر است.')
    
    context = {
        'user': user,
        'user_role': user_role,
        'role_choices': UserRole.ROLE_CHOICES,
    }
    
    return render(request, 'dashboard/edit_user_role.html', context)


@admin_required
@require_http_methods(["POST"])
def delete_user(request, user_id):
    """حذف کاربر"""
    user = get_object_or_404(User, pk=user_id)
    username = user.username
    
    # جلوگیری از حذف خود کاربر
    if user.id == request.user.id:
        messages.error(request, '❌ نمی‌توانید خود را حذف کنید.')
        return redirect('dashboard:manage-users')
    
    user.delete()
    messages.success(request, f'✅ کاربر {username} حذف شد.')
    
    return redirect('dashboard:manage-users')


@admin_required
@require_http_methods(["POST"])
def toggle_user_status(request, user_id):
    """فعال/غیرفعال کردن کاربر"""
    user = get_object_or_404(User, pk=user_id)
    
    # جلوگیری از غیرفعال کردن خود کاربر
    if user.id == request.user.id:
        messages.error(request, '❌ نمی‌توانید وضعیت خود را تغییر دهید.')
        return redirect('dashboard:manage-users')
    
    user.is_active = not user.is_active
    user.save()
    
    status = 'فعال' if user.is_active else 'غیرفعال'
    messages.success(request, f'✅ کاربر {user.username} {status} شد.')
    
    return redirect('dashboard:manage-users')


# جزئیات آماری
@admin_required
def analytics_posts(request):
    """جزئیات آماری پست‌ها"""
    posts = BlogPost.objects.select_related('author').order_by('-published_at')
    
    # فیلترکردن
    status_filter = request.GET.get('status')
    if status_filter in ['published', 'draft', 'archived']:
        posts = posts.filter(status=status_filter)
    
    # آمار
    total = posts.count()
    published = posts.filter(status='published').count()
    draft = posts.filter(status='draft').count()
    archived = posts.filter(status='archived').count()
    
    context = {
        'posts': posts[:50],  # صفحه‌بندی
        'total': total,
        'published': published,
        'draft': draft,
        'archived': archived,
        'status_filter': status_filter,
    }
    
    return render(request, 'dashboard/analytics_posts.html', context)


@admin_required
def analytics_comments(request):
    """جزئیات آماری نظرات"""
    comments = BlogComment.objects.select_related('post', 'user').order_by('-created_at')
    
    # فیلترکردن
    approval_filter = request.GET.get('approval')
    if approval_filter == 'approved':
        comments = comments.filter(is_approved=True)
    elif approval_filter == 'pending':
        comments = comments.filter(is_approved=False)
    
    # آمار
    total = comments.count()
    approved = comments.filter(is_approved=True).count()
    pending = comments.filter(is_approved=False).count()
    
    context = {
        'comments': comments[:50],
        'total': total,
        'approved': approved,
        'pending': pending,
        'approval_filter': approval_filter,
    }
    
    return render(request, 'dashboard/analytics_comments.html', context)


@admin_required
def analytics_messages(request):
    """جزئیات آماری پیام‌های تماس"""
    messages_list = ContactMessage.objects.order_by('-created_at')
    
    # فیلترکردن
    read_filter = request.GET.get('read')
    if read_filter == 'read':
        messages_list = messages_list.filter(is_read=True)
    elif read_filter == 'unread':
        messages_list = messages_list.filter(is_read=False)
    
    # آمار
    total = messages_list.count()
    read = messages_list.filter(is_read=True).count()
    unread = messages_list.filter(is_read=False).count()
    answered = messages_list.filter(is_replied=True).count()
    
    context = {
        'messages': messages_list[:50],
        'total': total,
        'read': read,
        'unread': unread,
        'answered': answered,
        'read_filter': read_filter,
    }
    
    return render(request, 'dashboard/analytics_messages.html', context)


@admin_required
def analytics_users(request):
    """جزئیات آماری کاربران"""
    from django.contrib.auth.models import User
    
    users = User.objects.all().select_related('user_role').order_by('-date_joined')
    
    # فیلترکردن
    status_filter = request.GET.get('status')
    if status_filter == 'active':
        users = users.filter(is_active=True)
    elif status_filter == 'inactive':
        users = users.filter(is_active=False)
    
    # آمار
    total = users.count()
    active = users.filter(is_active=True).count()
    inactive = users.filter(is_active=False).count()
    staff = users.filter(is_staff=True).count()
    
    context = {
        'users': users[:50],
        'total': total,
        'active': active,
        'inactive': inactive,
        'staff': staff,
        'status_filter': status_filter,
    }
    
    return render(request, 'dashboard/analytics_users.html', context)


@admin_required
def blog_posts(request):
    """مدیریت پست‌های بلاگ در پنل ادمین"""
    from django.core.paginator import Paginator
    
    posts = BlogPost.objects.select_related('author', 'category').order_by('-created_at')
    
    # فیلترکردن
    status_filter = request.GET.get('status')
    author_filter = request.GET.get('author')
    category_filter = request.GET.get('category')
    
    if status_filter and status_filter in ['published', 'draft', 'archived']:
        posts = posts.filter(status=status_filter)
    elif status_filter == 'active':
        posts = posts.filter(is_active=True)
    elif status_filter == 'inactive':
        posts = posts.filter(is_active=False)
    
    if author_filter:
        try:
            posts = posts.filter(author_id=int(author_filter))
        except:
            pass
    
    if category_filter:
        try:
            posts = posts.filter(category_id=int(category_filter))
        except:
            pass
    
    # Pagination
    paginator = Paginator(posts, 12)
    page = request.GET.get('page', 1)
    posts_page = paginator.get_page(page)
    
    # آمار
    total = BlogPost.objects.count()
    published = BlogPost.objects.filter(status='published').count()
    draft = BlogPost.objects.filter(status='draft').count()
    archived = BlogPost.objects.filter(status='archived').count()
    active = BlogPost.objects.filter(is_active=True).count()
    inactive = BlogPost.objects.filter(is_active=False).count()
    
    # لیست نویسندگان و دسته‌بندی‌ها برای فیلتر
    from blog.models import BlogCategory
    authors = User.objects.filter(blogpost__isnull=False).distinct()
    categories = BlogCategory.objects.all()
    
    context = {
        'posts': posts_page,
        'total': total,
        'published': published,
        'draft': draft,
        'archived': archived,
        'active': active,
        'inactive': inactive,
        'status_filter': status_filter,
        'author_filter': author_filter,
        'category_filter': category_filter,
        'authors': authors,
        'categories': categories,
        'title': 'مدیریت پست‌های بلاگ',
    }
    
    return render(request, 'dashboard/blog_posts.html', context)

