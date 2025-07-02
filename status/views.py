from datetime import date
from django.shortcuts import render
from rest_framework import viewsets, mixins, status
from .serializers import *
from utils.responses import custom_response
from rest_framework.decorators import action
import os, environ
from pathlib import Path
import requests

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
        elif self.action == 'year':
            return NationDashboardYearSerializer
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
    
    @action(detail=False, methods=['get'], url_path='year')
    def year(self, request):
        queryset =self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return custom_response(data=serializer.data)

class LocalDashViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    queryset = LocalDashboard.objects.all()
    serializer_class = LocalDashboardSerializer

    def filter_by_local(self, queryset):
        local_name = self.request.query_params.get('local')
        if local_name:
            queryset = queryset.filter(local__local_name=local_name)
        return queryset
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return self.filter_by_local(queryset)

    def get_serializer_class(self):
        if self.action == 'map':
            return LocalDashboardMapSerializer
        elif self.action == 'city':
            return LocalDashboardCitySerializer
        elif self.action == 'city_ranking':
            return LocalDashboardCityRankingSerializer
        elif self.action == 'major_exchange':
            return LocalDashboardMajorSerializer
        elif self.action == 'vision':
            return LocalDashboardVisionSerializer
        return LocalDashboardSerializer
    
    @action(detail=False, methods=['get'], url_path='map')
    def map(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return custom_response(data=serializer.data)
    
    @action(detail=False, methods=['get'], url_path='city')
    def city(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return custom_response(data=serializer.data)
    
    @action(detail=False, methods=['get'], url_path='city-ranking')
    def city_ranking(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return custom_response(data=serializer.data)
    
    @action(detail=False, methods=['get'], url_path='major-exchange')
    def major_exchange(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return custom_response(data=serializer.data)
    
    @action(detail=False, methods=['get'], url_path='vision')
    def vision(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return custom_response(data=serializer.data)
    

# 공공 데이터 가져오기
BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(os.path.join(BASE_DIR,'.env'))
NATION_DATA_KEY_3 = env('NATION_DATA_KEY_3')


from datetime import date

class ExchangeDataAPI(viewsets.ViewSet):

    @action(detail=False, methods=['post'])
    def load_public_data_3(self, request):
        url = f"https://api.odcloud.kr/api/15069220/v1/uddi:ca27bf6d-9bea-45c6-b96b-fd4ee98175f6?page=10&perPage=10&returnType=json&serviceKey={NATION_DATA_KEY_3}"
        response = requests.get(url)
        if response.status_code != 200:
            return custom_response(data=None, code=400, message="잘못된 요청입니다.", success=False)

        raw_data = response.json().get("data", [])

        saved = []
        failed = []

        for idx, item in enumerate(raw_data, start=1):
            try:
                # 콩고 민주공화국 데이터만 저장
                if "베트남" not in item.get("사업대상지", ""):
                    continue

                # 지원분야 → exchange_category 변환
                field = item.get("지원분야", "")
                if "기술" in field:
                    category = "health"
                elif "교육" in field:
                    category = "edu"
                elif "문화" in field:
                    category = "culture"
                elif "제도" in field or "행정" in field:
                    category = "system"
                else:
                    category = "etc"

                # Nation 연결
                nation_name_field = item.get("사업대상지", "")
                if "베트남" in nation_name_field:
                    nation_name = "베트남"
                else:
                    nation_name = nation_name_field.split()[0] if nation_name_field else None

                if not nation_name:
                    failed.append({"index": idx, "reason": "사업대상지에서 국가명이 없음", "item": item})
                    continue

                nation = Nation.objects.filter(nation_name__icontains=nation_name).first()
                if not nation:
                    failed.append({"index": idx, "reason": f"Nation 객체를 찾을 수 없음 (nation_name: {nation_name})", "item": item})
                    continue

                # 필수값 체크 (예: 교류명)
                exchange_name_kr = item.get("사업명(국문)")
                if not exchange_name_kr:
                    failed.append({"index": idx, "reason": "사업명(국문) 값 없음", "item": item})
                    continue

                # 저장 또는 업데이트
                obj, created = ExchangeData.objects.update_or_create(
                    exchange_name_kr=exchange_name_kr,
                    exchange_nation=nation,
                    defaults={
                        "exchange_name_en": item.get("사업명(영문)"),
                        "exchange_category": category,
                        "exchange_content": item.get("사업내용") or item.get("사업목적"),
                        "start_year": item.get("사업기간(시작연도)"),
                        "end_year": item.get("사업기간(종료연도)"),
                        "others": f"""
                            성과: {item.get('성과(OUTCOME)', '')}
                            산출물: {item.get('산출물(OUTPUT)', '')}
                            예산: {item.get('사업예산(만불)', '')}
                            수행기관: {item.get('사업수행기관', '')}
                        """,
                        "pub_date": date.today()
                    }
                )
                saved.append({"index": idx, "id": obj.exchange_id, "created": created})

            except Exception as e:
                failed.append({"index": idx, "reason": str(e), "item": item})

        return custom_response(
            data={
                "saved_count": len(saved),
                "failed_count": len(failed),
                "saved": saved,
                "failed": failed,
                "message": "데이터 저장 작업 완료"
            },
            code=200,
            message="완료"
        )
