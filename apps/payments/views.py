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
           # ✅ FIX: Add time so it is always unique (e.g., TEMP-2-1-17039283)
            transaction_id=f"TEMP-{request.user.id}-{property.id}-{int(time.time())}" 
        )

        # Call M-Pesa (Using the class above)
        gate = MpesaGate()
        amount = int(property.price) 
        reference = f"House {property.id}"
        
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
            
    return render(request, 'payments/initiate_payment.html', {'property': property})

@csrf_exempt
def mpesa_callback(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print("M-Pesa Callback:", data)
            # You can add logic here later to find the Payment by CheckoutRequestID and mark it PAID
        except:
            pass
        return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})
    
    return JsonResponse({"error": "Method not allowed"})