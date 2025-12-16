
# Create your models here.
import uuid
from django.db import models
from django.conf import settings
from urllib.parse import quote
from django.utils.text import slugify

# 1. Choices (Dropdowns for the Admin Panel)
PROPERTY_TYPES = (
    ('SINGLE', 'Single Room'),
    ('BEDSITTER', 'Bedsitter'),
    ('1BED', 'One Bedroom'),
    ('2BED', 'Two Bedroom'),
    ('3BED', 'Three Bedroom +'),
    ('SHOP', 'Commercial/Shop'),
)

WATER_SOURCES = (
    ('MAWASCO', 'Council Water (Mawasco)'),
    ('BOREHOLE', 'Salty/Borehole'),
    ('FRESH_TANK', 'Fresh Water Tank'),
    ('NONE', 'No Water Connection'),
)

class Property(models.Model):
    """
    The main house listing.
    """

    @property  # <--- This is the Magic Decorator
    def whatsapp_link(self):
        try:
            # 1. Get Phone (Default to admin if missing)
            raw_phone = str(self.contact_phone)
            if not raw_phone or raw_phone == "None":
                print("DEBUG: Phone is missing!") # Check your terminal for this
                return "https://wa.me/254700000000"

            # 2. Clean it
            cleaned = "".join(filter(str.isdigit, raw_phone))
            
            # 3. Format it
            if cleaned.startswith("0"):
                final_phone = "254" + cleaned[1:]
            elif cleaned.startswith("254"):
                final_phone = cleaned
            else:
                final_phone = "254" + cleaned

            # 4. Generate Link
            msg = f"Hi, I am interested in {self.title}"
            encoded_msg = quote(msg)
            
            link = f"https://wa.me/{final_phone}?text={encoded_msg}"
            
            print(f"DEBUG: Generated Link: {link}") # <--- LOOK FOR THIS IN TERMINAL
            return link
            
        except Exception as e:
            print(f"DEBUG ERROR: {e}") # <--- TELLS US IF CODE CRASHED
            return "https://wa.me/"
        
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # We link the house to a specific User (The Landlord/Agent)
    landlord = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='properties')
    
    title = models.CharField(max_length=255, help_text="e.g. Spacious 1 Bedroom near Mazeras High School")
    slug = models.SlugField(unique=True, blank=True, max_length=255)
    description = models.TextField(blank=True)
    
    # Location Logic
    location_area = models.CharField(max_length=100, default="Mazeras Central")
    google_maps_link = models.CharField(max_length=500, blank=True, help_text="Paste Google Maps pin link here")
    distance_to_highway = models.DecimalField(max_digits=4, decimal_places=1, help_text="Distance in KM", null=True, blank=True)

    # Financials (Using Decimal for accuracy)
    rent_amount = models.DecimalField(max_digits=10, decimal_places=2)
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    contact_phone = models.CharField(max_length=15, help_text="e.g. 0712345678 (For WhatsApp)", default="0700000000")
    
    # Specifics
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPES, default='SINGLE')
    water_source = models.CharField(max_length=20, choices=WATER_SOURCES, default='MAWASCO')
    has_token_electricity = models.BooleanField(default=True, verbose_name="KPLC Token")
    is_tiled = models.BooleanField(default=False)
    
    # Status
    is_available = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False, help_text="Checked by Makazi Link Team?")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Auto-generate a SEO-friendly link (slug) if it doesn't exist
        if not self.slug:
            self.slug = slugify(self.title) + "-" + str(uuid.uuid4())[:8]
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} - KES {self.rent_amount}"

    class Meta:
        verbose_name_plural = "Properties"

class PropertyImage(models.Model):
    """
    Allows multiple photos per house.
    """
    property = models.ForeignKey(Property, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='property_photos/%Y/%m/')
    is_feature = models.BooleanField(default=False, help_text="Is this the main photo?")

    def get_whatsapp_link(self):
        phone = str(self.contact_phone)
        
        # 1. Clean the number (Remove spaces, dashes, brackets)
        cleaned_phone = "".join(filter(str.isdigit, phone))
        
        # 2. Format to 254...
        if cleaned_phone.startswith("0"):
            final_phone = "254" + cleaned_phone[1:]
        elif cleaned_phone.startswith("254"):
            final_phone = cleaned_phone
        else:
            final_phone = "254" + cleaned_phone # Fallback
            
        # 3. Create the link
        message = f"Hi, I'm interested in {self.title}"
        return f"https://wa.me/{final_phone}?text={quote(message)}"

    def __str__(self):
        return f"Image for {self.property.title}"
