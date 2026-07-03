from django.urls import path, re_path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.blog_list, name='blog-list'),
    path('create/', views.blog_create, name='blog-create'),
    re_path(r'^post/(?P<slug>[\w-]+)/$', views.blog_detail, name='post-detail'),
    re_path(r'^post/(?P<slug>[\w-]+)/edit/$', views.blog_edit, name='post-edit'),
    re_path(r'^post/(?P<slug>[\w-]+)/delete/$', views.blog_delete, name='post-delete'),
    path('category/<str:category>/', views.blog_category, name='blog-category'),
]
