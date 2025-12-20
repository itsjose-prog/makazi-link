from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import requests
import json
import base64
import time
from datetime import datetime
from apps.core.models import Property
from .models import Payment

# ==========================================
# 1. THE MPESA GATE CLASS
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
            response.raise_for_status()
            return response.json().get('access_token')
        except Exception as e:
            print(f"M-Pesa Auth Error: {str(e)}")
            return None

    def trigger_stk_push(self, phone_number, amount, reference):
        token = self.get_access_token()
        if not token:
            return {"error": "Authentication Failed", "errorMessage": "Could not get token"}

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
    
    # Define the viewing fee
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
            amount=VIEWING_FEE,  # Use the fee, not the property price
            phone_number=phone_number,
            status='PENDING',
            transaction_id=f"TEMP-{request.user.id}-{property.id}-{int(time.time())}" 
        )

        # Call M-Pesa
        gate = MpesaGate()
        reference = f"House {property.id}"
        
        # Trigger STK Push with the viewing fee (100)
        response = gate.trigger_stk_push(phone_number, VIEWING_FEE, reference)

        if response.get('ResponseCode') == '0':
            messages.success(request, f"STK Push sent! Please pay KES {VIEWING_FEE} on your phone.")
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
            
    return render(request, 'payments/initiate_payment.html', {'property': property, 'fee': VIEWING_FEE})

@csrf_exempt
def mpesa_callback(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print("📩 M-Pesa Callback Received:", data)

            stk_callback = data.get('Body', {}).get('stkCallback', {})
            checkout_id = stk_callback.get('CheckoutRequestID')
            result_code = stk_callback.get('ResultCode')

            payment = Payment.objects.filter(transaction_id=checkout_id).first()

            if payment:
                if result_code == 0:
                    payment.status = 'COMPLETED'
                    print(f"✅ Payment {checkout_id} marked as COMPLETED.")
                else:
                    payment.status = 'FAILED'
                    print(f"❌ Payment {checkout_id} failed.")
                payment.save()

        except Exception as e:
            print(f"🔥 Error processing callback: {str(e)}")

        return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})
    
    return JsonResponse({"error": "Method not allowed"})