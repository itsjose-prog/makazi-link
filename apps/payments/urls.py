from django.urls import path
from . import views

urlpatterns = [
    # This is the page where they enter their phone number
    path('initiate/<int:property_id>/', views.initiate_payment, name='initiate_payment'),
    
    # This is where Safaricom sends the "Success" message
    path('callback/', views.mpesa_callback, name='mpesa_callback'),
]