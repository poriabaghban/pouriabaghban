from django.urls import path

from . import views


app_name = "downloads"

urlpatterns = [
    path("", views.downloads_home, name="home"),
    path("category/<slug:slug>/", views.category_detail, name="category_detail"),
    path("item/<slug:slug>/", views.item_detail, name="item_detail"),
    path("file/<slug:slug>/", views.download_file, name="download_file"),
    path("item/<slug:slug>/react/", views.react, name="react"),
    path("login/", views.FrontendLoginView.as_view(), name="login"),
    path("logout/", views.frontend_logout, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
]
