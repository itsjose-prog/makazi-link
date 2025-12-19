
# Register your models here.
from django.contrib import admin
from .models import Property

# 1. Customize the Text (This changes "Django Administration")
admin.site.site_header = "Makazi Link Administration"  # Login Page Top
admin.site.site_title = "Makazi Admin"                 # Browser Tab
admin.site.index_title = "Management Console"          # Dashboard Title

# 2. Register Property so you can manage houses
@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'location', 'price', 'landlord', 'created_at')
    search_fields = ('title', 'location')
    list_filter = ('location', 'bedrooms')
