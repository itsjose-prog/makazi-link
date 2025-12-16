
# Create your models here.
import uuid
from django.db import models
from apps.properties.models import Property # <--- We link back to the Property

PAYMENT_STATUS = (
    ('PENDING', 'Pending'),
    ('COMPLETED', 'Completed'),
    ('FAILED', 'Failed'),
    ('REFUNDED', 'Refunded'),
)

class ViewingRequest(models.Model):
    """
    Tracks who wants to see which house.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    seeker_name = models.CharField(max_length=100)
    seeker_phone = models.CharField(max_length=15)
    
    scheduled_time = models.DateTimeField(null=True, blank=True)
    has_paid_viewing_fee = models.BooleanField(default=False)
    
    outcome = models.CharField(
        max_length=20, 
        choices=(('PENDING', 'Pending'), ('VIEWED', 'Viewed'), ('SUCCESS', 'Rented')),
        default='PENDING'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Viewing: {self.seeker_name} -> {self.property.title}"

class PaymentTransaction(models.Model):
    """
    Tracks the Money.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    viewing_request = models.ForeignKey(ViewingRequest, on_delete=models.SET_NULL, null=True, related_name='transactions')
    
    mpesa_receipt_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    phone_number = models.CharField(max_length=15)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='PENDING')
    transaction_date = models.DateTimeField(auto_now_add=True)
    
    raw_response = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.phone_number} - {self.status}"
