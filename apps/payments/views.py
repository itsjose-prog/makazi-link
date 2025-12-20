from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json

# Import the Property model and our new MpesaClient
from apps.core.models import Property
from .models import Payment
from .mpesa import MpesaClient 

@login_required
def initiate_payment(request, property_id):
    property = get_object_or_404(Property, id=property_id)
    
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        
        # Basic validation
        if not phone_number:
            messages.error(request, "Please enter a phone number")
            return redirect('initiate_payment', property_id=property_id)

        # 1. Create a Pending Payment Record in Database
        payment = Payment.objects.create(
            payer=request.user,
            property=property,
            amount=property.price,
            phone_number=phone_number,
            status='PENDING',
            # We will update the transaction_id when Safaricom calls us back
            transaction_id=f"TEMP-{request.user.id}-{property.id}" 
        )

        # 2. Trigger M-Pesa STK Push
        client = MpesaClient()
        callback_url = settings.MPESA_CALLBACK_URL
        
        # Safaricom expects amounts as integers (no decimals)
        amount = int(property.price) 
        
        response = client.stk_push(phone_number, amount, callback_url)

        # 3. Check if Safaricom accepted the request
        if response.get('ResponseCode') == '0':
            messages.success(request, f"STK Push sent to {phone_number}. Check your phone to pay!")
            return redirect('dashboard')
        else:
            messages.error(request, f"M-Pesa Error: {response.get('errorMessage', 'Unknown error')}")
            # If it failed, maybe mark the payment as FAILED here
            payment.status = 'FAILED'
            payment.save()
            
    return render(request, 'payments/initiate_payment.html', {'property': property})

@csrf_exempt
def mpesa_callback(request):
    """
    Safaricom sends results here after the user enters their PIN (or cancels).
    """
    if request.method == 'POST':
        data = json.loads(request.body)
        
        # Log the response (Optional: Print to console to see what Safaricom sent)
        print("M-Pesa Callback:", data)
        
        # Logic to update the Payment model goes here
        # (We will add the detailed extraction logic in the next step)
        
        return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})
    
    return JsonResponse({"error": "Method not allowed"})