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

    def create(self, request, *args, **kwargs):
        print("Request data:", request.data)
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print("Errors:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
