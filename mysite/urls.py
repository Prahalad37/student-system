from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('members.urls')),  # ✅ Saara traffic members app par jayega
    # ❌ marksheet_pdf wali line YAHAN SE HATA DI HAI (Wo members/urls.py mein hai)
]

# Images/Media dikhane ke liye zaroori code
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)