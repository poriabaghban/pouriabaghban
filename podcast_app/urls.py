from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'podcast_app'

urlpatterns = [
    path('sheer/', views.podcast_list, name='sheer_list'),
    path('sheer/<int:podcast_id>/', views.podcast_detail, name='podcast_detail'),
    path('sheerwizhe/', views.special_poem_list, name='special_list'),
    path('sheerwizhe/<int:podcast_id>/', views.special_poem_detail, name='special_detail'),
    path('sheerwizhe/login/', views.special_login, name='special_login'),
    path('sheerwizhe/logout/', views.special_logout, name='special_logout'),
    path('podcast/', views.podcast_list, name='podcast_list'),
    path('podcast/audio-token/<int:podcast_id>/', views.generate_audio_token, name='audio_token'),
    path('podcast/secure-stream/<int:podcast_id>/', views.secure_audio_stream, name='secure_stream'),
    path('login/', auth_views.LoginView.as_view(template_name='podcast_app/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
]
