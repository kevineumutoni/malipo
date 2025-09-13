# api/views.py

from rest_framework import viewsets
from users.models import Member
from savings.models import SavingsAccount
from savings.models import SavingsContribution
from vsla.models import VSLA_Account
from .serializers import (
    SavingsAccountSerializer,
    SavingsContributionSerializer,
    VSLAAccountSerializer,
)
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.response import Response
from .serializers import PensionSerializer, PolicySerializer
from pension.models import Pension
from policy.models import Policy
from rest_framework import viewsets
from .serializers import PensionSerializer, PolicySerializer


class SavingsAccountViewSet(viewsets.ModelViewSet):
    queryset = SavingsAccount.objects.select_related("member").all()
    serializer_class = SavingsAccountSerializer
    lookup_field = "saving_id"


class SavingsContributionViewSet(viewsets.ModelViewSet):
    queryset = SavingsContribution.objects.select_related("saving__member").all()
    serializer_class = SavingsContributionSerializer
    lookup_field = "contribution_id"


class VSLAAccountViewSet(viewsets.ModelViewSet):
    queryset = VSLA_Account.objects.all()
    serializer_class = VSLAAccountSerializer
    lookup_field = "vsla_id"


class PensionViewSet(viewsets.ModelViewSet):
    queryset = Pension.objects.all()
    serializer_class = PensionSerializer

class PolicyViewSet(viewsets.ModelViewSet):
    queryset = Policy.objects.all()
    serializer_class = PolicySerializer

   
