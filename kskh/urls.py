from django.urls import path

from . import views


app_name = "kskh"

urlpatterns = [
    path("", views.index, name="index"),
    path("upload/", views.upload, name="upload"),
    path("login/", views.kskh_login, name="login"),
    path("api/login/", views.kskh_api_login, name="api_login"),
    path("logout/", views.kskh_logout, name="logout"),
    path("post/<slug:slug>/", views.detail, name="detail"),
    path("post/<slug:slug>/download/", views.download_file, name="download"),
    path("post/<slug:slug>/react/", views.react, name="react"),
    path("comment/<int:pk>/delete/", views.delete_comment, name="delete_comment"),
]
