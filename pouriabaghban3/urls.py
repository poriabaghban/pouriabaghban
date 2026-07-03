"""
URL configuration for pouriabaghban3 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.views.generic import RedirectView
from pages import views as pages_views

admin.site.site_header = 'Pouria Baghban Admin Panel'
admin.site.site_title = 'Site Admin'
admin.site.index_title = 'داشبورد مدیریت'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('downloads/', RedirectView.as_view(pattern_name='kskh:index', permanent=False)),
    path('downloads/<path:unused>/', RedirectView.as_view(pattern_name='kskh:index', permanent=False)),
    path('kskh/', include('kskh.urls')),
    path('admin-chat/', include('admin_chat.urls')),
    path('i18n/', include('django.conf.urls.i18n')),
    path('rosetta/', include('rosetta.urls')),
    path('.well-known/appspecific/com.chrome.devtools.json', lambda request: HttpResponse(status=204)),
]

urlpatterns += i18n_patterns(
    path('', include('podcast_app.urls')),
    path('', include('pages.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('blog/', include('blog.urls')),
    path('gallery/', include('gallery.urls')),
    path('', include('contact.urls')),
    path('', include('message.urls')),
    prefix_default_language=False,
)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Error handlers
handler400 = pages_views.error_400
handler403 = pages_views.error_403
handler404 = pages_views.error_404
handler500 = pages_views.error_500
