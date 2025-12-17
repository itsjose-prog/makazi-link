"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls')), # Core app URLs
    path('payments/', include('apps.payments.urls')), # Payments URLs
    path('accounts/', include('apps.accounts.urls')), # Accounts URLs
    path('properties/', include('apps.properties.urls')), # Properties URLs
]

# (Keep the static/media code at the bottom)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # --- TEMPORARY ADMIN FIX START ---
from django.urls import path
from django.http import HttpResponse
from django.contrib.auth import get_user_model

def fix_admin_view(request):
    try:
        User = get_user_model()
        # Create or Get the admin user
        user, created = User.objects.get_or_create(username='admin')
        
        # FORCE the password to be admin123
        user.set_password('admin123')
        user.email = 'admin@example.com'
        user.is_staff = True
        user.is_superuser = True
        user.save()
        
        status = "CREATED NEW" if created else "UPDATED EXISTING"
        return HttpResponse(f"<h1>SUCCESS!</h1><p>User: admin</p><p>Password: admin123</p><p>Status: {status}</p>")
    except Exception as e:
        return HttpResponse(f"<h1>ERROR</h1><p>{str(e)}</p>")

# Add this specific URL to your patterns
urlpatterns += [
    path('fix-admin-now/', fix_admin_view),
]
# --- TEMPORARY ADMIN FIX END ---