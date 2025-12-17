from django.db import models
from django.conf import settings  # <--- NEW: Import settings
from django.utils.text import slugify

class Property(models.Model):
    # FIXED: Use settings.AUTH_USER_MODEL instead of 'User'
    landlord = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    # Basic House Details
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    location = models.CharField(max_length=100)
    
    # Amenities
    bedrooms = models.IntegerField(default=1)
    bathrooms = models.IntegerField(default=1)
    
    # Image
    image = models.ImageField(upload_to='properties/')
    
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title