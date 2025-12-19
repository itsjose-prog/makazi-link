from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Core App (This handles Home, Dashboard, and Properties now)
    path('', include('apps.core.urls')),
    
    # Accounts App (Login/Signup)
    path('accounts/', include('apps.accounts.urls')),
    
    # Payments App
    path('payments/', include('apps.payments.urls')),
    
    # ❌ DELETED: path('properties/', include('apps.properties.urls')), 
    # (We removed this line because it was causing the crash)
]

# This allows images to load in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)