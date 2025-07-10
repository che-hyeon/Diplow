from datetime import datetime
from django.shortcuts import render
from rest_framework import viewsets, mixins
from rest_framework.views import APIView
from rest_framework.decorators import action
from .serializers import *
from utils.responses import custom_response
from status.serializers import NationSerializer

from main.models import MovementData
from main.serializers import MovementDataKRSerializer

import os, environ
from pathlib import Path
import requests

import json

from django.template.loader import render_to_string
from django.http import HttpResponse
import pdfkit

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
    
# GPT 호출
import openai
from openai import OpenAI
from django.conf import settings

class PublicDiplomacyGPTView(APIView):
    def post(self, request):
        local = request.data.get("local", "")
        if not local:
            return custom_response(data=None, message="local field는 필수 입니다.", code=400, success=False)
        nation = request.data.get("nation", "")
        if not nation:
            return custom_response(data=None, message="nation field는 필수 입니다.", code=400, success=False)
        category = request.data.get("category", "")
        if not category:
            return custom_response(data=None, message="category field는 필수 입니다.", code=400, success=False)
        purpose = request.data.get("purpose", "")
        if not purpose:
            return custom_response(data=None, message="purpose field는 필수 입니다.", code=400, success=False)
        client = OpenAI(api_key=getattr(settings, "GPT_API_KEY"))

        full_message = (
            f"지방자치단체: {local}\n"
            f"탐색 대상 국가: {nation}\n"
            f"교류 분야: {category}\n"
            f"협력 목적: {purpose}\n\n"
            "위 정보를 바탕으로 전략 보고서를 JSON 형식으로 작성해 주세요.\n"
            "JSON 구조는 다음과 같습니다:\n"
            "{\n"
            '  "recommended_strategy_types": [\n'
            '    {"type": "유형명", "description": "설명"}\n'
            '  ],\n'
            '  "exchange_cooperation_projects": [\n'
            '    {"project_name": "사업명", "project_category": "사업 유형", "description": "100자 내외 설명"}\n'
            '  ],\n'
            '  "summary_of_recommendations": {\n'
            '    "major_issues_by_country": "300자 내외 설명",\n'
            '    "local_government_diplomatic_assets": "300자 내외 설명",\n'
            '    "case_study_based_analysis": "300자 내외 설명"\n'
            '  }\n'
            "}\n"
            "응답은 반드시 JSON 형식으로, 코드블록 없이 순수 JSON 텍스트로만 보내 주세요."
        )

        try:
            completion = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "당신은 지방외교 및 도시외교 전략 전문가입니다\n"
                            "사용자는 지방자치단체의 국제협력 실무자이며, 특정 지자체의 교류 이력과 탐색 국가의 동향 바탕으로 교류 전략 보고서를 희망합니다\n"
                            "사용자의 선택값(지자체, 대상국가, 교류 분야, 협력 목적)을 기반으로 형식을 갖춘 명료한 전략 보고서를 아래의 양식에 맞춰 작성해 주세요\n"
                            "1. 추천 교류 전략 유형: 자매결연, 교류외교, 기여외교, 매체외교, 문화외교 중 가장 적합한 외교 유형 2가지를 선택, 선택된 유형의 정의(100자 내외)와 함께 서술.\n"
                            "2. 교류 협력 사업 제안: 교류 전략 수립 관련 인사이트를 바탕으로 사용자의 선택값을 충족하는 지방자치단체에 효과적이고 퀄리티 있는 국제교류 및 협력사업의 예시를 유형과 100자 내외의 설명을 포함하여 3가지 제안.\n"
                            " ※ 2번 항목의 사업 유형은 국제 행사, 시민 포럼, 해외 자매도시 초청, MOU, 성과공유회, 상징사업, 공동사업, 연구사업, 전문가 교류, 청소년/청년 방문 사절 프로그램 등의 예시를 참고하여 예시 외에도 실제 시행 가능한 구체적이고 다양한 유형으로 표현.\n"
                            "3. 추천 근거 요약.zip: 1) 국가별 주요 이슈 동향, 2) 우리 지자체 외교 자산, 3) 기존 사례 기반 분석을 골자로 제시."
                            "- 국가별 주요 이슈 동향: 탐색 대상 국가의 주요 이슈를 설명.\n"
                            "- 우리 지자체 외교 자산: 선택한 지자체가 보유한 외교적 자산에 관해 설명.\n"
                            "- 기존 사례 기반 분석: 교류 협력 사업 제안의 탐색에 사용되었던 기존의 실제 협력 사례들을 설명.\n\n"
                            "※ 3번 항목의 세 가지 소항목은 각각 300자 내외로 자세히 작성해 주세요."
                        )
                    },
                    {"role": "user", "content": full_message}
                ]
            )

            answer = completion.choices[0].message.content
            parsed_answer = json.loads(answer)
            return custom_response(
                data=parsed_answer
            )

        except Exception as e:
            return custom_response(data={"error": str(e)}, code=500, success=False, message=str(e))
        
class MakePDFView(APIView):
    def post(self, request):
        local = request.data.get('local', '')
        nation = request.data.get('nation', '')

        if not local or not nation:
            return custom_response(data=None, message="local과 nation은 필수 필드 입니다.", code=400, success=False)

        strategy_types = request.data.get('recommended_strategy_types', [])
        if not isinstance(strategy_types, list):
            return custom_response(
                data=None,
                message="error: recommended_strategy_types는 리스트여야 합니다.",
                code=400,
                success=False
            )

        exchange_projects = request.data.get('exchange_cooperation_projects', [])
        if not isinstance(exchange_projects, list):
            return custom_response(
                data=None,
                message="error: exchange_cooperation_projects는 리스트여야 합니다.",
                code=400,
                success=False
            )

        summary_data = request.data.get('summary_of_recommendations', {})
        if not isinstance(summary_data, dict):
            return custom_response(
                data=None,
                message="error: summary_of_recommendations는 딕셔너리여야 합니다.",
                code=400,
                success=False
            )
        
        try:
            nation_obj = Nation.objects.get(nation_name=nation)
        except Nation.DoesNotExist:
            return custom_response(data=None, message="해당 국가를 찾을 수 없습니다.", code=404, success=False)

        general_overview = nation_obj.nation_info
        economic_overview = nation_obj.nation_economic
        relation_korea = nation_obj.nation_relation

        recent_movements_qs = MovementData.objects.filter(nation=nation_obj).order_by('-pub_date')[:4]
        recent_movements = MovementDataKRSerializer(recent_movements_qs, many=True).data

        environ_issues_qs = EnvironIssueData.objects.filter(nation=nation_obj).order_by('-pub_date')[:5]
        environ_issues = EnvironIssueDataSerializer(environ_issues_qs, many=True).data

        context = {
            'local': local,
            'nation': nation,
            'strategy_types': strategy_types,
            'exchange_projects': exchange_projects,
            'summary': summary_data,
            'general_overview': general_overview,
            'economic_overview': economic_overview,
            'relation_korea': relation_korea,
            'recent_movements': recent_movements,
            'environ_issues': environ_issues
        }

        html_string = render_to_string('recommend/pdf_template.html', context)

        local = env('LOCAL')
        if local == 'True':
            config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
        else:
            config = pdfkit.configuration(wkhtmltopdf='/usr/bin/wkhtmltopdf')
        pdf_output = pdfkit.from_string(html_string, False, configuration=config)

        response = HttpResponse(pdf_output, content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="report.pdf"'
        return response
