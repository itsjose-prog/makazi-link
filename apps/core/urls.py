from django.urls import path
from . import views  # <--- This is the only import you need

urlpatterns = [
    # Homepage
    path('', views.home, name='home'),

    # Property Details (e.g., /property/modern-apartment-voi/)
    path('property/<slug:slug>/', views.property_detail, name='property_detail'),

    # User Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),

    # Add Property Page (The one you were missing)
    path('add-property/', views.add_property, name='add_property'),
]