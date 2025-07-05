from datetime import datetime
from django.shortcuts import render
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from .serializers import *
from utils.responses import custom_response
from status.serializers import NationSerializer

import os, environ
from pathlib import Path
import requests
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
    

BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(os.path.join(BASE_DIR,'.env'))
NATION_DATA_KEY_3 = env('NATION_DATA_KEY_3')

class EnvironIssueDataAPI(viewsets.ViewSet):

    @action(detail=False, methods=['post'])
    def load_environ_data(self, request):
        base_url = "https://api.odcloud.kr/api/15130846/v1/uddi:16260f8b-fd43-42da-bb8a-dcba073c9a87"
        service_key = NATION_DATA_KEY_3
        per_page = 100
        page = 1

        saved = []
        failed = []

        nations = list(Nation.objects.all())

        count_url = f"{base_url}?page=1&perPage=1&returnType=json&serviceKey={service_key}"
        count_response = requests.get(count_url)
        if count_response.status_code != 200:
            return custom_response(data=None, code=400, message="페이지 수 확인 실패", success=False)

        total_count = count_response.json().get("totalCount", 0)
        total_pages = (total_count // per_page) + (1 if total_count % per_page else 0)

        for page in range(1, total_pages + 1):
            url = f"{base_url}?page={page}&perPage={per_page}&returnType=json&serviceKey={service_key}"
            response = requests.get(url)

            if response.status_code != 200:
                failed.append({"base_url": base_url, "page": page, "reason": "요청 실패"})
                continue

            raw_data = response.json().get("data", [])

            for idx, item in enumerate(raw_data, start=1):
                try:
                    environ_data_title = item.get("제목", "")
                    if not environ_data_title:
                        failed.append({"page": page, "index": idx, "reason": "제목 없음", "item": item})
                        continue

                    nation = next((n for n in nations if n.nation_name in environ_data_title), None)
                    if not nation:
                        failed.append({"page": page, "index": idx, "reason": f"제목에 해당하는 Nation 객체 없음", "item": item})
                        continue

                    pub_date = item.get("등록일", "").strip()

                    try:
                        agreement_date = datetime.strptime(pub_date, "%Y-%m-%d").date()
                    except ValueError:
                        continue  # 날짜 형식 이상하면 스킵

                    obj, created = EnvironIssueData.objects.update_or_create(
                        nation = nation,
                        environ_data_title = environ_data_title,
                        pub_date = agreement_date
                    )

                    saved.append({"base_url": base_url, "page": page, "index": idx, "id": obj.environ_data_id, "created": created})

                except Exception as e:
                    failed.append({"base_url": base_url, "page": page, "index": idx, "reason": str(e), "item": item})

        return custom_response(
            data={
                "saved_count": len(saved),
                "failed_count": len(failed),
                "message": "전체 페이지 데이터 저장 완료"
            },
            code=200,
            message="완료"
        )