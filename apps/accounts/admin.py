
# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    # Add our new fields to the "fieldsets" (The sections you see in Admin)
    fieldsets = UserAdmin.fieldsets + (
        ('Makazi Link Roles', {'fields': ('is_landlord', 'is_verified', 'phone_number')}),
    )
    
    # Add them to the "add user" page as well
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Makazi Link Roles', {'fields': ('is_landlord', 'phone_number')}),
    )

    # Columns to show in the list view
    list_display = ['username', 'email', 'phone_number', 'is_landlord', 'is_verified', 'is_staff']
    
    # Filters on the right sidebar
    list_filter = ['is_landlord', 'is_verified', 'is_staff']
    
    # Search bar capability
    search_fields = ['username', 'email', 'phone_number']

admin.site.register(User, CustomUserAdmin)
