from django.urls import path
from . import views

urlpatterns = [
    path('pay/<slug:property_slug>/', views.initiate_payment, name='initiate_payment'),
    # New Path for Safaricom to talk to:
    path('callback/', views.mpesa_callback, name='mpesa_callback'),
]