from django.urls import path
from . import views
from apps.core import views

urlpatterns = [
    path('', views.home, name='home'),
    # New Path: <slug:slug> grabs the text from the URL and sends it to the view
    path('property/<slug:slug>/', views.property_detail, name='property_detail'),
    # New Dashboard Path
    path('dashboard/', views.dashboard, name='dashboard'),
    path('add-property/', views.add_property, name='add_property'),
]