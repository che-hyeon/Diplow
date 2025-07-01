from django.shortcuts import render
from rest_framework import viewsets, mixins
from .serializers import *
from rest_framework.decorators import action
from utils.responses import custom_response
# Create your views here.

class TendDataKRViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    queryset = MovementData.objects.all().order_by('-pub_date')
    serializer_class = MovementDataKRSerializer

    def filter_by_nation(self, queryset):
        nation_name = self.request.query_params.get('nation')
        if nation_name:
            queryset = queryset.filter(nation__nation_name=nation_name)
        return queryset
    
    def get_queryset(self):
        return self.filter_by_nation(self.queryset)
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return custom_response(data=serializer.data)
    
class DiplomacyEventViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    queryset = DiplomacyEvent.objects.all().order_by('-created_at')
    serializer_class = DiplomacyEventSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return custom_response(data=serializer.data)