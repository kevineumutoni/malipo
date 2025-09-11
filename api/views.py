from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from transaction.models import Transaction 
from .serializers import TransactionSerializer 

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
   