
# Register your models here.
from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    # What columns to show in the list
    list_display = ('payer', 'property', 'amount', 'phone_number', 'status', 'transaction_id', 'created_at')
    
    # Add filters on the right side
    list_filter = ('status', 'created_at')
    
    # Add a search bar
    search_fields = ('transaction_id', 'phone_number', 'payer__username')
    
    # Make these fields read-only so you don't accidentally change history
    readonly_fields = ('created_at', 'transaction_id')
