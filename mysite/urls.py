from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from members.views.auth import TenantLoginView
from members.views.health import health

urlpatterns = [
    path('health/', health, name='health'),
    path('favicon.ico', RedirectView.as_view(url=settings.STATIC_URL + 'assets/img/brand/semora-logo.png', permanent=False)),
    path('admin/', admin.site.urls),
    path('', include('pwa.urls')),
    path('accounts/login/', TenantLoginView.as_view(), name='login'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('super-admin/', include('members.urls_super_admin')),  # NEW: Super Admin Portal
    path('', include('members.urls')),
]

# Images/Media dikhane ke liye zaroori code
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom error handlers
handler404 = 'members.views.errors.page_not_found'
handler500 = 'members.views.errors.server_error'