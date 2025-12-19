from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt # Needed for M-Pesa
from django.contrib import messages
from apps.core.models import Property  # <--- ✅ CORRECT IMPORT (From Core)
from .models import Payment

@login_required
def initiate_payment(request, property_id):
    property = get_object_or_404(Property, id=property_id)
    
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        
        # Create a Pending Payment Record
        payment = Payment.objects.create(
            payer=request.user,
            property=property,
            amount=property.price,
            phone_number=phone_number,
            status='PENDING',
            transaction_id=f"TXN-{request.user.id}-{property.id}"
        )
        
        messages.success(request, "Payment initiated! (Simulation)")
        return redirect('dashboard')
        
    return render(request, 'payments/initiate_payment.html', {'property': property})

# ✅ ADDED THIS MISSING FUNCTION
@csrf_exempt
def mpesa_callback(request):
    """
    This function listens for messages from Safaricom.
    For now, it just says 'OK' to prevent errors.
    """
    return JsonResponse({'ResultCode': 0, 'ResultDesc': 'Accepted'})