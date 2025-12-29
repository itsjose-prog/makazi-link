
# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Custom User Model for Makazi Link.
    Inherits from AbstractUser to keep Django's password hashing and permissions.
    """

    # --- NEW FEATURE: Role Choices (For the Dropdown) ---
    TENANT = 'tenant'
    LANDLORD = 'landlord'
    
    ROLE_CHOICES = [
        (TENANT, 'Tenant'),
        (LANDLORD, 'Landlord'),
    ]

    user_type = models.CharField(
        max_length=10, 
        choices=ROLE_CHOICES, 
        default=TENANT,
        help_text="Select account type: Tenant or Landlord"
    )
    # ----------------------------------------------------
    
    # Existing Fields (Kept exactly as they were)
    is_landlord = models.BooleanField(
        default=False, 
        help_text="Designates whether this user can list properties."
    )
    is_verified = models.BooleanField(
        default=False,
        help_text="Has this user's ID/Phone been manually verified?"
    )
    phone_number = models.CharField(
        max_length=15, 
        unique=True, 
        null=True, 
        blank=True,
        help_text="Required for M-Pesa transactions"
    )

    # We enforce email uniqueness
    email = models.EmailField(unique=True)

    # --- NEW FEATURE: Auto-Sync Logic ---
    # This magically keeps your old code working. 
    # If they pick "Landlord" in the dropdown, it sets is_landlord = True automatically.
    def save(self, *args, **kwargs):
        if self.user_type == self.LANDLORD:
            self.is_landlord = True
        else:
            self.is_landlord = False
        super().save(*args, **kwargs)

    def __str__(self):
        # Uses the nice readable name (e.g., "Tenant" instead of "tenant")
        return f"{self.username} ({self.get_user_type_display()})"