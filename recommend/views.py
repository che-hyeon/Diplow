from django.shortcuts import render
from rest_framework import viewsets, mixins
from .serializers import *
from utils.responses import custom_response
from status.serializers import NationSerializer
# Create your views here.

class EnvironIssueDataViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    queryset = EnvironIssueData.objects.all().order_by('-pub_date')
    serializer_class = EnvironIssueDataSerializer

    def filter_by_nation(self, queryset):
        nation_name = self.request.query_params.get('nation')
        if nation_name:
            queryset = queryset.filter(nation__nation_name=nation_name)
        return queryset
    
    def get_queryset(self):
        queryset = self.queryset
        queryset = self.filter_by_nation(queryset)
        return queryset[:5] 
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return custom_response(data=serializer.data)
    
class NationInfoViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    queryset = Nation.objects.all()
    serializer_class = NationSerializer

    def filter_by_nation(self, queryset):
        nation_name = self.request.query_params.get('nation')
        if nation_name:
            queryset = queryset.filter(nation_name=nation_name)
        return queryset
    
    def get_queryset(self):
        return self.filter_by_nation(self.queryset)
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return custom_response(data=serializer.data)