import requests
import base64
import datetime
from django.conf import settings
from requests.auth import HTTPBasicAuth

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
        try:
            response = requests.get(url, auth=HTTPBasicAuth(self.consumer_key, self.consumer_secret), timeout=10)
            response.raise_for_status()
            return response.json().get('access_token')
            
        except Exception:
            return None

    def stk_push(self, phone_number, amount, account_reference, transaction_desc):
        access_token = self.get_access_token()
        if not access_token:
            return {"error": "Failed to get access token"}
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
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def b2c_payment(self, phone_number, amount):
        access_token = self.get_access_token()
        if not access_token:
            return {"error": "Failed to get access token"}
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "InitiatorName": "testapi",
            "SecurityCredential": "Safaricom999!*!",
            "CommandID": "BusinessPayment",
            "Amount": str(int(amount)),
            "PartyA": self.business_shortcode,
            "PartyB": phone_number,
            "Remarks": "Loan Disbursement",
            "QueueTimeOutURL": f"{self.callback_url}/b2c-callback/",
            "ResultURL": f"{self.callback_url}/b2c-callback/",
            "Occasion": "LoanPayment"
        }
        url = f"{self.base_url}/mpesa/b2c/v1/paymentrequest"
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def b2b_payment(self, receiver_shortcode, amount):
        access_token = self.get_access_token()
        if not access_token:
            return {"error": "Failed to get access token"}
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "Initiator": "testapi",
            "SecurityCredential": "Safaricom999!*!",
            "CommandID": "BusinessPayment",
            "SenderIdentifierType": "4",
            "RecieverIdentifierType": "4",
            "Amount": str(int(amount)),
            "PartyA": self.business_shortcode,
            "PartyB": receiver_shortcode,
            "AccountReference": "PensionTransfer",
            "Remarks": "Pension contribution transfer",
            "QueueTimeOutURL": f"{self.callback_url}/b2b-callback/",
            "ResultURL": f"{self.callback_url}/b2b-callback/"
        }
        url = f"{self.base_url}/mpesa/b2b/v1/paymentrequest"
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            return response.json()
        except Exception as e:
            return {"error": str(e)}



           