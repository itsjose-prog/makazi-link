from django.db import models
from django.conf import settings
from django.utils.text import slugify

class Property(models.Model):
    # Link to the User model (Landlord)
    landlord = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='properties')
    
    # Basic Details
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    location = models.CharField(max_length=255)
    
    # House Specs
    bedrooms = models.IntegerField()
    bathrooms = models.IntegerField()
    
    # Contact Info (The field that was causing issues)
    contact_phone = models.CharField(
        max_length=20, 
        default='0712345678', 
        help_text="Landlord phone number for inquiries"
    )
    
    # Status & Media
    is_approved = models.BooleanField(default=False)
    image = models.ImageField(upload_to='property_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Auto-generate slug from title if it doesn't exist
        if not self.slug:
            self.slug = slugify(self.title)
            
        super().save(*args, **kwargs)

    def get_whatsapp_number(self):
        """
        Converts local phone numbers (07xx) to international format (2547xx)
        for WhatsApp API links.
        """
        phone = str(self.contact_phone).strip()
        
        # Remove any spaces or dashes
        phone = phone.replace(" ", "").replace("-", "")
        
        # If it starts with '0', replace with '254'
        if phone.startswith("0"):
            return "254" + phone[1:]
        
        # If it starts with '+', remove it
        if phone.startswith("+"):
            return phone[1:]
            
        return phone

    def __str__(self):
        return self.title