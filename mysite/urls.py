from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # ✅ PWA URLs (Mobile App "Install" Feature)
    # Isse browser ko manifest.json aur serviceworker.js milta hai
    path('', include('pwa.urls')),

    # Authentication (Login/Logout)
    path('accounts/', include('django.contrib.auth.urls')),

    # Main App URLs (Dashboard, Students, etc.)
    path('', include('members.urls')),
]

# Images/Media dikhane ke liye zaroori code
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)