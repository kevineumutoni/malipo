from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.response import Response
from .serializers import PensionSerializer, PolicySerializer
from pension.models import Pension
from policy.models import Policy
from rest_framework import viewsets
from .serializers import PensionSerializer, PolicySerializer


class PensionViewSet(viewsets.ModelViewSet):
    queryset = Pension.objects.all()
    serializer_class = PensionSerializer

class PolicyViewSet(viewsets.ModelViewSet):
    queryset = Policy.objects.all()
    serializer_class = PolicySerializer

   