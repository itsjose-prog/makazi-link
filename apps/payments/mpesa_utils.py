import requests
import json
import base64
from datetime import datetime
from django.conf import settings
from decouple import config

class MpesaGate:
    def __init__(self):
        self.consumer_key = config('MPESA_CONSUMER_KEY')
        self.consumer_secret = config('MPESA_CONSUMER_SECRET')
        self.shortcode = config('MPESA_SHORTCODE')
        self.passkey = config('MPESA_PASSKEY')
        self.base_url = "https://sandbox.safaricom.co.ke"

    def get_access_token(self):
        """
        Authenticate with Safaricom to get a temporary security token.
        """
        api_url = f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials"
        response = requests.get(api_url, auth=(self.consumer_key, self.consumer_secret))
        
        try:
            return response.json()['access_token']
        except KeyError:
            print("M-Pesa Auth Error:", response.text)
            return None

    def trigger_stk_push(self, phone_number, amount, reference):
        """
        The magic function that makes the phone vibrate.
        """
        token = self.get_access_token()
        if not token:
            return {"error": "Authentication Failed"}

        # 1. Format the phone number (Must be 2547...)
        if phone_number.startswith('0'):
            phone_number = '254' + phone_number[1:]
        elif phone_number.startswith('+254'):
            phone_number = phone_number[1:]

        # 2. Generate Timestamp & Password
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password_str = f"{self.shortcode}{self.passkey}{timestamp}"
        password = base64.b64encode(password_str.encode()).decode()

        # 3. The Payload (Data sent to Safaricom)
        payload = {
            "BusinessShortCode": self.shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(amount), # M-Pesa doesn't like decimals
            "PartyA": phone_number,
            "PartyB": self.shortcode,
            "PhoneNumber": phone_number,
            "CallBackURL": config('MPESA_CALLBACK_URL'),
            "AccountReference": reference, # e.g., "House 4"
            "TransactionDesc": "Viewing Fee"
        }

        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

        api_url = f"{self.base_url}/mpesa/stkpush/v1/processrequest"
        response = requests.post(api_url, json=payload, headers=headers)
        
        return response.json()