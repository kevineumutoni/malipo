import requests
from django.conf import settings
from requests.auth import HTTPBasicAuth
import base64
import datetime
class DarajaAPI:
   def __init__(self):
       self.consumer_key = settings.DARAJA_CONSUMER_KEY
       self.consumer_secret = settings.DARAJA_CONSUMER_SECRET
       self.business_shortcode = settings.DARAJA_SHORTCODE
       self.passkey = settings.DARAJA_PASSKEY
       self.base_url = "https://sandbox.safaricom.co.ke"
       self.callback_url = settings.DARAJA_CALLBACK_URL
   def get_access_token(self):
       url = f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials"
       response = requests.get(url, auth=HTTPBasicAuth(self.consumer_key, self.consumer_secret))
       return response.json()['access_token']
   def stk_push(self, phone_number, amount, account_reference, transaction_desc):
       access_token = self.get_access_token()
       timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
       password = base64.b64encode(f"{self.business_shortcode}{self.passkey}{timestamp}".encode()).decode()
       headers = {
           "Authorization": f"Bearer {access_token}",
           "Content-Type": "application/json"
       }
       payload = {
           "BusinessShortCode": self.business_shortcode,
           "Password": password,
           "Timestamp": timestamp,
           "TransactionType": "CustomerPayBillOnline",
           "Amount": int(amount),
           "PartyA": phone_number,
           "PartyB": self.business_shortcode,
           "PhoneNumber": phone_number,
           "CallBackURL": self.callback_url,
           "AccountReference": account_reference, 
           "TransactionDesc": transaction_desc,
       }
       url = f"{self.base_url}/mpesa/stkpush/v1/processrequest"
       response = requests.post(url, headers=headers, json=payload)
       return response.json()


def get_access_token(self):
    url = f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials"
    try:
        response = requests.get(url, auth=HTTPBasicAuth(self.consumer_key, self.consumer_secret), timeout=10)
        response.raise_for_status()
        return response.json().get('access_token')
    except Exception as e:
        print(f"Token Error: {str(e)}")
        return None