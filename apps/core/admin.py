from django.contrib import admin
from .models import Property

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    # 1. WHAT TO SHOW: The columns you see in the list
    list_display = ('title', 'landlord', 'price', 'location', 'is_approved', 'created_at')
    
    # 2. QUICK EDIT: Toggle approval directly from the list!
    list_editable = ('is_approved',)
    
    # 3. FILTERS: Sidebar filters to quickly find "Pending" houses
    list_filter = ('is_approved', 'location', 'created_at')
    
    # 4. SEARCH: Search by House Title or Landlord Username
    search_fields = ('title', 'landlord__username', 'location')
    
    # 5. PAGINATION: 20 houses per page
    list_per_page = 20

    # Optional: Order by newest first
    ordering = ('-created_at',)