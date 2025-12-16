
# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Custom User Model for Makazi Link.
    Inherits from AbstractUser to keep Django's password hashing and permissions,
    but adds our specific business fields.
    """
    
    # We add these new fields to the standard Django user
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

    # We enforce email uniqueness (Django default allows duplicates)
    email = models.EmailField(unique=True)

    def __str__(self):
        # When we print a user, we want to see their username and role
        role = "Landlord" if self.is_landlord else "Tenant"
        return f"{self.username} ({role})"