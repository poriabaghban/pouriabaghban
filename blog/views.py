from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.utils import timezone
from django.utils.translation import get_language
from django.utils.translation import gettext as _
from django.db.models import F, Prefetch, Q
from django.views.decorators.csrf import ensure_csrf_cookie
from datetime import datetime
from .models import BlogPost, BlogComment, BlogTag
from .forms import BlogPostDetailImageFormSet, BlogPostForm
from dashboard.decorators import admin_required
from django.http import HttpResponseForbidden, Http404
from pages.models import SocialLink
from pouriabaghban3.input_validation import FORBIDDEN_USER_INPUT_MESSAGE, contains_forbidden_user_input


def language_content_filter(prefixes=("title", "content", "excerpt")):
    language = (get_language() or "fa").split("-")[0]
    suffix = language if language in ("en", "de") else "fa"
    query = Q()
    for prefix in prefixes:
        field = f"{prefix}_{suffix}"
        query &= Q(**{f"{field}__isnull": False}) & ~Q(**{field: ""})
    return query


def footer_social_url(platform, fallback):
    social = SocialLink.objects.filter(platform=platform, is_active=True).first()
    return social.url if social else fallback


def blog_list(request):
    query = request.GET.get('q', '').strip()
    selected_tag = request.GET.get('tag', '').strip()
    posts_queryset = BlogPost.objects.filter(status='published', is_active=True).filter(language_content_filter()).select_related('author', 'category').prefetch_related('tags')

    if query:
        language = (get_language() or "fa").split("-")[0]
        if language == "de":
            content_query = Q(title_de__icontains=query) | Q(excerpt_de__icontains=query) | Q(content_de__icontains=query)
        elif language == "en":
            content_query = Q(title_en__icontains=query) | Q(excerpt_en__icontains=query) | Q(content_en__icontains=query)
        else:
            content_query = Q(title_fa__icontains=query) | Q(excerpt_fa__icontains=query) | Q(content_fa__icontains=query) | Q(title__icontains=query) | Q(excerpt__icontains=query) | Q(content__icontains=query)
        posts_queryset = posts_queryset.filter(
            content_query
            | Q(category__name__icontains=query)
            | Q(tags__name__icontains=query)
        ).distinct()

    if selected_tag:
        posts_queryset = posts_queryset.filter(tags__slug=selected_tag).distinct()

    featured_post = posts_queryset.filter(is_featured=True).first()
    all_tags = BlogTag.objects.filter(blogpost__in=posts_queryset).distinct()
    paginator = Paginator(posts_queryset, 6)
    page = request.GET.get('page')
    posts = paginator.get_page(page)
    context = {
        'posts': posts,
        'featured_post': featured_post,
        'all_tags': all_tags,
        'query': query,
        'selected_tag': selected_tag,
        'total_posts': posts_queryset.count(),
        'title': _('بلاگ')
    }
    return render(request, 'blog/blog_list.html', context)


@ensure_csrf_cookie
def blog_detail(request, slug):
    post = get_object_or_404(BlogPost.objects.filter(language_content_filter()).prefetch_related('detail_images'), slug=slug, status='published', is_active=True)
    # increment view count
    post.views += 1
    post.save()
    approved_replies = BlogComment.objects.filter(is_approved=True).order_by("created_at")
    comments = (
        post.comments.filter(is_approved=True, parent__isnull=True)
        .prefetch_related(Prefetch("replies", queryset=approved_replies))
        .order_by("created_at")
    )
    approved_comments_count = post.comments.filter(is_approved=True).count()
    related_posts = BlogPost.objects.filter(status='published', is_active=True).filter(language_content_filter()).exclude(pk=post.pk)
    if post.category_id:
        related_posts = related_posts.filter(category=post.category)
    related_posts = related_posts.select_related('author', 'category')[:3]

    # handle comment form submission
    if request.method == 'POST':
        if request.POST.get("action") == "like":
            BlogPost.objects.filter(pk=post.pk).update(likes=F("likes") + 1)
            messages.success(request, _('لایک شما ثبت شد.'))
            return redirect('blog:post-detail', slug=post.slug)

        author = request.POST.get('name')
        email = request.POST.get('email')
        content = request.POST.get('content')
        parent = None
        parent_id = request.POST.get('reply_to')
        if parent_id:
            parent = post.comments.filter(pk=parent_id, parent__isnull=True, is_approved=True).first()
        if author and email and content:
            if any(contains_forbidden_user_input(value) for value in (author, email, content)):
                messages.error(request, FORBIDDEN_USER_INPUT_MESSAGE)
                return redirect('blog:post-detail', slug=post.slug)
            BlogComment.objects.create(post=post, parent=parent, author=author, email=email, content=content, is_approved=True)
            language = (get_language() or "fa").split("-")[0]
            if language == "en":
                success_message = "Your reply has been posted." if parent else "Your comment has been posted."
            elif language == "de":
                success_message = "Ihre Antwort wurde veröffentlicht." if parent else "Ihr Kommentar wurde veröffentlicht."
            else:
                success_message = "پاسخ شما ثبت شد." if parent else "نظر شما ثبت شد."
            messages.success(request, success_message)
            return redirect('blog:post-detail', slug=post.slug)
        else:
            messages.error(request, _('لطفاً تمام فیلدها را پر کنید.'))

    context = {
        'post': post,
        'detail_images': post.detail_images.all(),
        'comments': comments,
        'approved_comments_count': approved_comments_count,
        'related_posts': related_posts,
        'telegram_url': footer_social_url("telegram", "https://telegram.me/pb369000000"),
        'linkedin_url': footer_social_url(
            "linkedin",
            "https://www.linkedin.com/in/pouria-baghban-914477380?utm_source=share&utm_campaign=share_via&utm_content=profile&utm_medium=android_app",
        ),
        'title': post.get_title()
    }
    return render(request, 'blog/blog_detail.html', context)


@admin_required
def blog_create(request):
    """ایجاد پست جدید"""
    # بررسی اینکه آیا کاربر می‌تواند پست ایجاد کند
    try:
        if not (request.user.is_staff or request.user.user_role.can_write):
            messages.error(request, '❌ شما اجازه ایجاد پست ندارید.')
            return redirect('blog:blog-list')
    except:
        if not request.user.is_staff:
            messages.error(request, '❌ شما اجازه ایجاد پست ندارید.')
            return redirect('blog:blog-list')
    
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES)
        image_formset = BlogPostDetailImageFormSet(request.POST, request.FILES)
        if form.is_valid() and image_formset.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            
            # تنظیم تاریخ انتشار اگر وضعیت منتشر است
            if post.status == 'published' and not post.published_at:
                post.published_at = timezone.now()
            
            post.save()
            form.save_m2m()  # ذخیره ManyToMany tags
            image_formset.instance = post
            image_formset.save()
            
            messages.success(request, _('Post "%(title)s" was created successfully.') % {'title': post.get_title()})
            if post.status == 'published' and post.is_active:
                return redirect('blog:post-detail', slug=post.slug)
            return redirect('blog:post-edit', slug=post.slug)
        else:
            messages.error(request, _('Please correct the errors below.'))
    else:
        form = BlogPostForm()
        image_formset = BlogPostDetailImageFormSet()
    
    context = {
        'form': form,
        'image_formset': image_formset,
        'title': _('Create new post'),
        'is_create': True,
    }
    return render(request, 'blog/blog_form.html', context)


@admin_required
def blog_edit(request, slug):
    """ویرایش پست - فقط برای کاربران دارای اجازه تغیی"""
    post = get_object_or_404(BlogPost, slug=slug)
    
    # بررسی اینکه آیا کاربر می‌تواند این پست را ویرایش کند
    if post.author != request.user and not request.user.is_staff:
        messages.error(request, '❌ شما اجازه ویرایش این پست ندارید.')
        return redirect('blog:post-detail', slug=post.slug)
    
    # بررسی اجازه ویرایش
    try:
        if not (request.user.is_staff or request.user.user_role.can_edit):
            messages.error(request, '❌ شما اجازه ویرایش پست ندارید.')
            return redirect('blog:post-detail', slug=post.slug)
    except:
        if not request.user.is_staff:
            messages.error(request, '❌ شما اجازه ویرایش پست ندارید.')
            return redirect('blog:post-detail', slug=post.slug)
    
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES, instance=post)
        image_formset = BlogPostDetailImageFormSet(request.POST, request.FILES, instance=post)
        if form.is_valid() and image_formset.is_valid():
            post = form.save(commit=False)
            
            # تنظیم تاریخ انتشار اگر وضعیت تغییر کرد
            if post.status == 'published' and not post.published_at:
                post.published_at = timezone.now()
            elif post.status != 'published':
                post.published_at = None
            
            post.save()
            form.save_m2m()
            image_formset.save()
            
            messages.success(request, _('Post "%(title)s" was updated successfully.') % {'title': post.get_title()})
            if post.status == 'published' and post.is_active:
                return redirect('blog:post-detail', slug=post.slug)
            return redirect('blog:post-edit', slug=post.slug)
        else:
            messages.error(request, _('Please correct the errors below.'))
    else:
        form = BlogPostForm(instance=post)
        image_formset = BlogPostDetailImageFormSet(instance=post)
    
    context = {
        'form': form,
        'image_formset': image_formset,
        'post': post,
        'title': _('Edit: %(title)s') % {'title': post.get_title()},
        'is_create': False,
    }
    return render(request, 'blog/blog_form.html', context)


@admin_required
@permission_required('blog.delete_blogpost', raise_exception=True)
def blog_delete(request, slug):
    """حذف پست - فقط برای کاربران دارای اجازه حذف"""
    post = get_object_or_404(BlogPost, slug=slug)
    
    # بررسی اجازه حذف
    if post.author != request.user and not request.user.is_staff:
        messages.error(request, '❌ شما اجازه حذف این پست ندارید.')
        return redirect('blog:post-detail', slug=post.slug)
    
    try:
        if not (request.user.is_staff or request.user.user_role.can_delete):
            messages.error(request, '❌ شما اجازه حذف پست ندارید.')
            return redirect('blog:post-detail', slug=post.slug)
    except:
        if not request.user.is_staff:
            messages.error(request, '❌ شما اجازه حذف پست ندارید.')
            return redirect('blog:post-detail', slug=post.slug)
    
    if request.method == 'POST':
        title = post.title
        post.delete()
        messages.success(request, f'✅ پست "{title}" با موفقیت حذف شد.')
        return redirect('blog:blog-list')
    
    context = {
        'post': post,
        'title': f'حذف: {post.title}',
    }
    return render(request, 'blog/blog_delete.html', context)


def blog_category(request, category):
    posts = BlogPost.objects.filter(status='published', is_active=True).filter(language_content_filter())
    context = {
        'posts': posts,
        'category': category,
        'title': _('بلاگ - %(category)s') % {'category': category}
    }
    return render(request, 'blog/blog_list.html', context)







