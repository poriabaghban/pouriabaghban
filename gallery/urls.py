from django.urls import path
from . import views

app_name = 'gallery'

urlpatterns = [
    path('', views.gallery_list, name='gallery-list'),
    path('portfolio/', views.portfolio_list, name='portfolio-list'),
    path('portfolio/category/<str:category>/', views.portfolio_category, name='portfolio-category'),
    path('portfolio/<int:pk>/', views.portfolio_detail, name='portfolio-detail'),
    path('category/<str:category>/', views.gallery_category, name='gallery-category'),
]
