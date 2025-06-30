from django.shortcuts import render
from rest_framework import viewsets, mixins, status
from .serializers import *
from utils.responses import custom_response
from rest_framework.decorators import action

# Create your views here.

class NationDashViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    queryset = NationDashboard.objects.all()
    serializer_class = NationDashboardMapSerializer
    
    def filter_by_nation(self, queryset):
        nation_name = self.request.query_params.get('nation')
        if nation_name:
            queryset = queryset.filter(nation__nation_name=nation_name)
        return queryset

    def get_queryset(self):
        queryset = super().get_queryset()
        return self.filter_by_nation(queryset)
        
    def get_serializer_class(self):
        # 요청 경로에 따라 serializer 변경
        if self.action == 'map':
            return NationDashboardMapSerializer
        elif self.action == 'category':
            return NationDashboardCategorySerializer
        elif self.action == 'recent':
            return NationDashboardRecentSerializer
        # 기본 serializer
        return NationDashboardMapSerializer

    @action(detail=False, methods=['get'], url_path='map')
    def map(self, request):
        # 기본 list와 같은 serializer, 필터링 사용
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return custom_response(data=serializer.data)

    @action(detail=False, methods=['get'], url_path='category-ratio')
    def category(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return custom_response(data=serializer.data)
    
    @action(detail=False, methods=['get'], url_path='recent')
    def recent(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return custom_response(data=serializer.data)