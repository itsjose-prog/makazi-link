from django.urls import path
from . import views

urlpatterns = [
    path('add/', views.add_property, name='add_property'),
    path('all/', views.all_properties, name='all_properties'),
]