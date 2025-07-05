from django.shortcuts import render
from rest_framework import viewsets, mixins
from rest_framework.response import Response
from .serializers import *
from rest_framework.decorators import action
from utils.responses import custom_response
from status.models import Nation
from . tasks import load_movement_data_task

import re
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
        queryset = self.get_queryset()[:4]
        serializer = self.get_serializer(queryset, many=True)
        return custom_response(data=serializer.data)
    
class DiplomacyEventViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    queryset = DiplomacyEvent.objects.all().order_by('-created_at')
    serializer_class = DiplomacyEventSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return custom_response(data=serializer.data)
    

class MovementDataAPI(viewsets.ViewSet):

    @action(detail=False, methods=['post'])
    def load_movement_data(self, request):
        load_movement_data_task.delay()  # 비동기 실행
        return Response({"message": "작업이 백그라운드에서 시작되었습니다."})