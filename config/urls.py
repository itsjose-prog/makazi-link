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

# Note: We removed 'from apps.core import views' because we don't need it here anymore.

urlpatterns = [
    path('admin/', admin.site.urls),

    # --- THE CORE APP ---
    # This single line handles Home, Add-Property, Dashboard, and Property Details.
    # It tells Django: "Go look at apps/core/urls.py for the list."
    path('', include('apps.core.urls')), 

    # --- OTHER APPS (Untouched) ---
    path('payments/', include('apps.payments.urls')),
    path('accounts/', include('apps.accounts.urls')),
    path('properties/', include('apps.properties.urls')),
]

# Media & Static Helper (For images to work)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

   