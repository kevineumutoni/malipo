# api/views.py

from rest_framework import viewsets
from users.models import Member
from savings.models import SavingsAccount
from savings.models import SavingsContribution
from vsla.models import VSLA_Account
from .serializers import (
    MemberSerializer,
    SavingsAccountSerializer,
    SavingsContributionSerializer,
    VSLAAccountSerializer
)

class MemberViewSet(viewsets.ModelViewSet):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer
    lookup_field = 'member_id'


class SavingsAccountViewSet(viewsets.ModelViewSet):
    queryset = SavingsAccount.objects.select_related('member').all()
    serializer_class = SavingsAccountSerializer
    lookup_field = 'saving_id'


class SavingsContributionViewSet(viewsets.ModelViewSet):
    queryset = SavingsContribution.objects.select_related('saving__member').all()
    serializer_class = SavingsContributionSerializer
    lookup_field = 'contribution_id'


class VSLAAccountViewSet(viewsets.ModelViewSet):
    queryset = VSLA_Account.objects.all()
    serializer_class = VSLAAccountSerializer
    lookup_field = 'vsla_id'