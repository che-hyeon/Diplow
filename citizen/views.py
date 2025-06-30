from django.shortcuts import render
from rest_framework import viewsets, mixins, status
from .serializers import *
from utils.pagination import ThreePerPagePagination
from utils.responses import custom_response
# Create your views here.

class OpinionViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin):
    queryset = Opinion.objects.all().order_by('-created_at')
    serializer_class = OpinionSerializer
    # pagination_class = ThreePerPagePagination 

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        local_name = self.request.query_params.get('local')
        if local_name:
            queryset = queryset.filter(local__local_name=local_name)
        return queryset
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return custom_response(
            data=serializer.data,
            message="의견 목록 조회 성공",
            code=status.HTTP_200_OK,
            success=True
        )
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            self.perform_create(serializer)
            return custom_response(
                data=[{"message": "게시 성공하였습니다."}],
                message="Success",
                code=status.HTTP_201_CREATED,
                success=True
            )
        else:
            return custom_response(
                data=[{"message": "게시 실패하였습니다."}],
                message="Validation Error",
                code=status.HTTP_400_BAD_REQUEST,
                success=False
            )
        
class ProgramViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    queryset = Program.objects.all().order_by('-created_at')
    serializer_class = ProgramSerializer
    # pagination_class = ThreePerPagePagination 

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        local_name = self.request.query_params.get('local')
        if local_name:
            queryset = queryset.filter(local__local_name=local_name)
        return queryset
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return custom_response(
            data=serializer.data,
            message="행사 목록 조회 성공",
            code=status.HTTP_200_OK,
            success=True
        )