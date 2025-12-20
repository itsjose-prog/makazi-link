from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    
    # ✅ CHANGE THIS LINE: Use <int:id> instead of <slug:slug>
    path('property/<int:id>/', views.property_detail, name='property_detail'),
    
    path('add/', views.add_property, name='add_property'),
    path('dashboard/', views.dashboard, name='dashboard'),
]