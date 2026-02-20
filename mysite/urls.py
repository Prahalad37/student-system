from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from members.views.auth import TenantLoginView
from members.views.health import health

urlpatterns = [
    path('health/', health, name='health'),
    path('admin/', admin.site.urls),
    path('', include('pwa.urls')),
    path('accounts/login/', TenantLoginView.as_view(), name='login'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('super-admin/', include('members.urls_super_admin')),  # NEW: Super Admin Portal
    path('', include('members.urls')),
]

# --- DEBUG TOOLBAR DISABLED FOR CLEANER UI ---
# if settings.DEBUG:
#     import debug_toolbar
#     urlpatterns += [
#         path('__debug__/', include(debug_toolbar.urls)),
#     ]

# Images/Media dikhane ke liye zaroori code  
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Custom error handlers
handler404 = 'members.views.errors.page_not_found'
handler500 = 'members.views.errors.server_error'