from django.contrib import admin
from django.urls import path, include
from django.conf import settings             # <--- Yeh line check karo
from django.conf.urls.static import static   # <--- Yeh line check karo

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('members.urls')),       # Aapka app URL config
]

# Yeh code development mode mein images dikhane ke liye ZAROORI hai
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)