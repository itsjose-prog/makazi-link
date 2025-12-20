from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import requests
import json
import base64
from datetime import datetime
from apps.core.models import Property
from .models import Payment
import time

# ==========================================
# 1. THE MPESA GATE CLASS (Moved Inside)
# ==========================================
class MpesaGate:
    def __init__(self):
        self.consumer_key = settings.MPESA_CONSUMER_KEY
        self.consumer_secret = settings.MPESA_CONSUMER_SECRET
        self.shortcode = settings.MPESA_SHORTCODE
        self.passkey = settings.MPESA_PASSKEY
        self.base_url = "https://sandbox.safaricom.co.ke"

    def get_access_token(self):
        api_url = f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials"
        try:
            response = requests.get(api_url, auth=(self.consumer_key, self.consumer_secret))
            response.raise_for_status() # Raise error for bad status codes
            return response.json().get('access_token')
        except Exception as e:
            print(f"M-Pesa Auth Error: {str(e)}")
            return None

    def trigger_stk_push(self, phone_number, amount, reference):
        token = self.get_access_token()
        if not token:
            return {"error": "Authentication Failed", "errorMessage": "Could not get token"}

        # Format Phone Number
        if phone_number.startswith('0'):
            phone_number = '254' + phone_number[1:]
        elif phone_number.startswith('+254'):
            phone_number = phone_number[1:]

        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password_str = f"{self.shortcode}{self.passkey}{timestamp}"
        password = base64.b64encode(password_str.encode()).decode()

        payload = {
            "BusinessShortCode": self.shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(amount),
            "PartyA": phone_number,
            "PartyB": self.shortcode,
            "PhoneNumber": phone_number,
            "CallBackURL": settings.MPESA_CALLBACK_URL,
            "AccountReference": reference,
            "TransactionDesc": "Viewing Fee"
        }

        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

        try:
            api_url = f"{self.base_url}/mpesa/stkpush/v1/processrequest"
            response = requests.post(api_url, json=payload, headers=headers)
            return response.json()
        except Exception as e:
            return {"error": "Request Failed", "errorMessage": str(e)}

# ==========================================
# 2. THE VIEWS
# ==========================================

@login_required
def initiate_payment(request, property_id):
    property = get_object_or_404(Property, id=property_id)

    #Define the specific viewing fee
    VIEWING_FEE = 100
    
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        
        if not phone_number:
            messages.error(request, "Please enter a phone number")
            return redirect('initiate_payment', property_id=property_id)

        # Create record
        payment = Payment.objects.create(
            payer=request.user,
            property=property,
            amount=VIEWING_FEE, #Use the Fee, NOT property.price
            amount=property.price,
            phone_number=phone_number,
            status='PENDING',
           #Add time so it is always unique (e.g., TEMP-2-1-17039283)
            transaction_id=f"TEMP-{request.user.id}-{property.id}-{int(time.time())}" 
        )

        # Call M-Pesa (Using the class above)
        gate = MpesaGate()
        amount = int(property.price) 
        reference = f"House {property.id}"
        #send 100 Bob to M-Pesa, not the Rent amount
        response = gate.trigger_stk_push(phone_number, VIEWING_FEE, reference) 
        
        response = gate.trigger_stk_push(phone_number, amount, reference)

        # Check response
        if response.get('ResponseCode') == '0':
            messages.success(request, f"STK Push sent to {phone_number}. Check your phone!")
            # Save the CheckoutRequestID if available, useful for tracking
            checkout_id = response.get('CheckoutRequestID')
            if checkout_id:
                payment.transaction_id = checkout_id
                payment.save()
            return redirect('dashboard')
        else:
            error_msg = response.get('errorMessage', 'Connection error')
            messages.error(request, f"M-Pesa Error: {error_msg}")
            payment.status = 'FAILED'
            payment.save()
            
    # Pass the fee to the template so the user sees "100"
    return render(request, 'payments/initiate_payment.html', {'property': property, 'fee': VIEWING_FEE})

@csrf_exempt
def mpesa_callback(request):
    """
    Safaricom calls this automatically when the user finishes entering their PIN.
    """
    if request.method == 'POST':
        try:
            # 1. Parse the incoming JSON from Safaricom
            data = json.loads(request.body)
            print("📩 M-Pesa Callback Received:", data) # Check your Render logs to see this!

            # 2. Extract the Data we need
            stk_callback = data.get('Body', {}).get('stkCallback', {})
            checkout_id = stk_callback.get('CheckoutRequestID')
            result_code = stk_callback.get('ResultCode') # 0 = Success, others = Fail
            result_desc = stk_callback.get('ResultDesc')

            # 3. Find the matching Payment in our Database
            # We use the 'checkout_id' because we saved it when we started the payment
            payment = Payment.objects.filter(transaction_id=checkout_id).first()

            if payment:
                if result_code == 0:
                    # ✅ SUCCESS! User paid.
                    payment.status = 'COMPLETED'
                    print(f"✅ Payment {checkout_id} marked as COMPLETED.")
                    
                    # OPTIONAL: You could mark the House as 'Taken' here if you wanted!
                    # payment.property.is_available = False
                    # payment.property.save()
                else:
                    # ❌ FAILED (User cancelled, insufficient funds, etc.)
                    payment.status = 'FAILED'
                    print(f"❌ Payment {checkout_id} failed: {result_desc}")

                payment.save()
            else:
                print(f"⚠️ Warning: Callback received for unknown CheckoutID: {checkout_id}")

        except Exception as e:
            print(f"🔥 Error processing callback: {str(e)}")

        # Always tell Safaricom "We got it" so they stop retrying
        return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})
    
    return JsonResponse({"error": "Method not allowed"})