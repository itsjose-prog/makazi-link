from django.db import models
from django.conf import settings  # <--- CHANGED: Import settings instead of User
from django.utils.text import slugify

class Property(models.Model):
    # CHANGED: Use settings.AUTH_USER_MODEL instead of User
    # This makes Django happy because it's the "official" way to link to users
    landlord = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='properties')
    
    title = models.CharField(max_length=255)
    is_approved = models.BooleanField(default=False)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    location = models.CharField(max_length=255)
    bedrooms = models.IntegerField()
    bathrooms = models.IntegerField()
    
    # Image is mandatory, but we allow blank=True temporarily
    image = models.ImageField(upload_to='property_images/', blank=True, null=True)
    
    slug = models.SlugField(unique=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

        # ... inside class Property ...

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