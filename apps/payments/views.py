from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from apps.core.models import Property
from .models import Payment
from .mpesa import MpesaGate  # <--- Imports the class from the file above

@login_required
def initiate_payment(request, property_id):
    property = get_object_or_404(Property, id=property_id)
    
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        
        if not phone_number:
            messages.error(request, "Please enter a phone number")
            return redirect('initiate_payment', property_id=property_id)

        # Create record
        payment = Payment.objects.create(
            payer=request.user,
            property=property,
            amount=property.price,
            phone_number=phone_number,
            status='PENDING',
            transaction_id=f"TEMP-{request.user.id}-{property.id}" 
        )

        # Call M-Pesa
        gate = MpesaGate()
        amount = int(property.price) 
        reference = f"House {property.id}"
        
        response = gate.trigger_stk_push(phone_number, amount, reference)

        if response.get('ResponseCode') == '0':
            messages.success(request, f"STK Push sent to {phone_number}. Check your phone to pay!")
            return redirect('dashboard')
        else:
            messages.error(request, f"M-Pesa Error: {response.get('errorMessage', 'Unknown error')}")
            payment.status = 'FAILED'
            payment.save()
            
    return render(request, 'payments/initiate_payment.html', {'property': property})

@csrf_exempt
def mpesa_callback(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        print("M-Pesa Callback:", data)
        return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})
    
    return JsonResponse({"error": "Method not allowed"})