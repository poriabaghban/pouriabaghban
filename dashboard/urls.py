from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard, name='index'),
    path('api/stats/', views.dashboard_api, name='api-stats'),
    path('admin-home/', views.admin_dashboard_home, name='admin-home'),
    
    # مدیریت کاربران
    path('users/', views.manage_users, name='manage-users'),
    path('users/<int:user_id>/edit-role/', views.edit_user_role, name='edit-user-role'),
    path('users/<int:user_id>/delete/', views.delete_user, name='delete-user'),
    path('users/<int:user_id>/toggle-status/', views.toggle_user_status, name='toggle-user-status'),
    
    # جزئیات آماری
    path('analytics/posts/', views.analytics_posts, name='analytics-posts'),
    path('analytics/comments/', views.analytics_comments, name='analytics-comments'),
    path('analytics/messages/', views.analytics_messages, name='analytics-messages'),
    path('analytics/users/', views.analytics_users, name='analytics-users'),
    
    # مدیریت بلاگ
    path('blog/posts/', views.blog_posts, name='blog-posts'),
]

