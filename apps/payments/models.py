from django.db import models
from django.conf import settings
# We now import Property from 'core', because that is where it lives now.
from apps.core.models import Property 

class Payment(models.Model):
    # Link to the user who is paying (Tenant/Student)
    payer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments')
    
    # Link to the property being paid for
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='payments')
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=15) # M-Pesa number
    
    # Status of the payment
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.payer.username} - {self.amount} - {self.status}"