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

    def __str__(self):
        return self.title