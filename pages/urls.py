from django.urls import path
from . import views

app_name = 'pages'

urlpatterns = [
    path('', views.home_page, name='home'),
    path('testimonials.json', views.testimonials_json, name='testimonials_json'),
    path('submit-comment/', views.submit_home_comment, name='submit_home_comment'),
    path('set-language/', views.set_language_from_storage, name='set_language_from_storage'),
]

