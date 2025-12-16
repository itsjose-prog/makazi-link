
# Register your models here.
from django.contrib import admin
from .models import Property, PropertyImage

class PropertyImageInline(admin.TabularInline):
    # This allows you to upload photos directly inside the Property page
    model = PropertyImage
    extra = 1

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ['title', 'rent_amount', 'location_area', 'is_available', 'is_verified']
    list_filter = ['is_available', 'is_verified', 'property_type', 'location_area']
    search_fields = ['title', 'location_area']
    inlines = [PropertyImageInline] # Add images while creating the property!

admin.site.register(PropertyImage)
