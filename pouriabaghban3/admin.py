from django.contrib import admin
from django.urls import path


class CustomAdminSite(admin.AdminSite):
    site_header = "pouriabaghban admin"
    site_title = "Site admin"
    index_title = "Admin dashboard"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard-home/', self.admin_site_dashboard, name='dashboard-home'),
        ]
        return custom_urls + urls

    def admin_site_dashboard(self, request):
        from dashboard.views import admin_dashboard_home
        return admin_dashboard_home(request)

    def index(self, request, extra_context=None):
        from blog.models import BlogAuthor, BlogComment, BlogPost
        from contact.models import ContactMessage

        extra_context = extra_context or {}
        extra_context.update({
            'total_posts': BlogPost.objects.count(),
            'published_posts': BlogPost.objects.filter(status='published').count(),
            'total_comments': BlogComment.objects.count(),
            'pending_comments': BlogComment.objects.filter(is_approved=False).count(),
            'total_messages': ContactMessage.objects.count(),
            'unread_messages': ContactMessage.objects.filter(is_read=False).count(),
            'total_authors': BlogAuthor.objects.filter(is_active=True).count(),
        })
        return super().index(request, extra_context)


admin_site = CustomAdminSite(name='custom_admin')