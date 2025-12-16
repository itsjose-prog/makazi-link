
# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from apps.properties.models import Property
from apps.payments.models import PaymentTransaction, ViewingRequest
from .mpesa_utils import MpesaGate

# For handling Safaricom callbacks
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import PaymentTransaction, ViewingRequest

def initiate_payment(request, property_slug):
    """
    1. Creates a Viewing Request
    2. Triggers M-Pesa STK Push
    """
    property_obj = get_object_or_404(Property, slug=property_slug)
    
    if request.method == 'POST':
        phone = request.POST.get('phone') # Get phone from the form
        
        # 1. Create the Viewing Request (Record that they want to see it)
        viewing = ViewingRequest.objects.create(
            property=property_obj,
            seeker_name="Guest User", # We can update this later
            seeker_phone=phone,
            scheduled_time="2025-12-20 10:00:00" # Placeholder for now
        )
        
        # 2. Trigger M-Pesa
        mpesa = MpesaGate()
        # Viewing fee is hardcoded to KES 1 for testing (Don't waste money yet!)
        response = mpesa.trigger_stk_push(phone, 1, f"View {property_obj.title[:10]}")
        
        # 3. Log the attempt
        if response.get('ResponseCode') == '0':
            # Success - Safaricom accepted the request
            PaymentTransaction.objects.create(
                viewing_request=viewing,
                phone_number=phone,
                amount=1,
                status='PENDING',
                raw_response=response
            )
            messages.success(request, f"Check your phone ({phone}). Enter PIN to complete booking.")
        else:
            messages.error(request, "Failed to connect to M-Pesa. Try again.")
            
        return redirect('property_detail', slug=property_slug)
    
    return redirect('home')


@csrf_exempt # Security Exception: Allow Safaricom to post data to us without a browser cookie
def mpesa_callback(request):
    if request.method == 'POST':
        try:
            # 1. Get the Data from Safaricom
            body = request.body.decode('utf-8')
            data = json.loads(body)
            
            # 2. Extract the Result
            # Safaricom sends nested JSON. We dig for the status code.
            stk_callback = data['Body']['stkCallback']
            result_code = stk_callback['ResultCode'] # 0 = Success, Others = Fail
            merchant_request_id = stk_callback['MerchantRequestID']
            checkout_request_id = stk_callback['CheckoutRequestID']
            
            # 3. Find the Transaction in our Database
            # (In a real app, we would match IDs. For now, we find the latest pending one for simplicity)
            # *PRO TIP: Ideally, save checkout_request_id when you initiate the push to match exactly.*
            transaction = PaymentTransaction.objects.filter(status='PENDING').last()

            if transaction:
                # Save the raw data for debugging
                transaction.raw_response = data
                
                if result_code == 0:
                    # SUCCESS!
                    transaction.status = 'COMPLETED'
                    transaction.mpesa_receipt_number = stk_callback['CallbackMetadata']['Item'][1]['Value']
                    
                    # Update the Viewing Request too
                    if transaction.viewing_request:
                        transaction.viewing_request.has_paid_viewing_fee = True
                        transaction.viewing_request.save()
                else:
                    # FAILED (User cancelled, insufficient funds, etc)
                    transaction.status = 'FAILED'
                
                transaction.save()

            return JsonResponse({"ResultCode": 0, "ResultDesc": "Received"})
        
        except Exception as e:
            print(f"Error processing callback: {e}")
            return JsonResponse({"ResultCode": 1, "ResultDesc": "Failed"})
            
    return JsonResponse({"ResultCode": 1, "ResultDesc": "Method not allowed"})