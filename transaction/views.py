from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.http import JsonResponse
import json
from rest_framework.decorators import api_view
from .daraja import DarajaAPI
from .serializers import STKPushSerializer
from .models import Transaction  
from django.conf import settings
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Transaction



class STKPushView(APIView):
    def post(self, request):
        serializer = STKPushSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        trans = Transaction.objects.create(
            transaction_type='C2B',
            amount_transacted=data['amount'],
            account_type='savings', 
            payment_transaction_status='initiated',
            callback_url=settings.DARAJA_CALLBACK_URL,
            created_at=timezone.now()
        )

        daraja = DarajaAPI()
        response = daraja.stk_push(
            phone_number=data['phone_number'],
            amount=data['amount'],
            account_reference=data['account_reference'],
            transaction_desc=data['transaction_desc']
        )

        if isinstance(response, dict) and response.get('ResponseCode') == '0':
            trans.payment_transaction_status = 'processing'
            trans.checkout_request_id = response.get('CheckoutRequestID', '')
        else:
            trans.payment_transaction_status = 'failed'
        trans.save()

        return Response(response)

@api_view(['POST'])
def daraja_callback(request):

    try:
        data = json.loads(request.body)
        result_code = data.get('Body', {}).get('stkCallback', {}).get('ResultCode')
        checkout_request_id = data.get('Body', {}).get('stkCallback', {}).get('CheckoutRequestID')

        if not checkout_request_id:
            return JsonResponse({"ResultCode": 1, "ResultDesc": "Missing CheckoutRequestID"}, status=400)

        trans = Transaction.objects.filter(checkout_request_id=checkout_request_id).first()
        if not trans:
            return JsonResponse({"ResultCode": 1, "ResultDesc": "Transaction not found"}, status=404)

        if result_code == 0:
            trans.payment_transaction_status = 'success'
            trans.completed_at = timezone.now()
        else:
            trans.payment_transaction_status = 'failed'

        trans.save()
        return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})

    except Exception as e:
        print(f"Callback Error: {str(e)}")
        return JsonResponse({"ResultCode": 1, "ResultDesc": "Internal Error"}, status=500)