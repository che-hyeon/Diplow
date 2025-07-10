from datetime import date, datetime
from django.shortcuts import render
from rest_framework import viewsets, mixins, status
from .serializers import *
from utils.responses import custom_response
from rest_framework.decorators import action
import os, environ
from pathlib import Path
import requests
import re

# Create your views here.

class NationDashViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    queryset = NationDashboard.objects.all()
    serializer_class = NationDashboardMapSerializer
    
    def filter_by_nation(self, queryset):
        nation_name = self.request.query_params.get('nation')
        if nation_name:
            queryset = queryset.filter(nation__nation_name__icontains=nation_name)
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
SEOUL_API_KEY = env('SEOUL_API_KEY')

def extract_korean_only(text):
    return ''.join(re.findall(r'[가-힣]+', text))

health_keywords = ["기술", "보건", "환경", "감염병", "재난", "대응", "시스템", "ICT", "기자재", "폐기물", "스마트", "에너지", "정보", "분석", "대응지침", "운영지침"]
edu_keywords = ["교육", "역량", "한국학", "콘텐츠", "커리큘럼", "연수", "교수요원", "평가", "프로그램", "학습", "훈련", "교육과정", "자격증"]
culture_keywords = ["문화", "관광", "한류", "커뮤니티", "참여", "사회통합", "한국어", "언어", "전시", "예술", "지역사회", "인식개선", "시민행사", "외교"]
system_keywords = ["정책", "제도", "부동산", "시스템", "행정", "모니터링", "평가", "수립", "전문가 파견", "법제도", "정보관리", "사업관리", "포용"]

class ExchangeDataAPI(viewsets.ViewSet):

    @action(detail=False, methods=['post'])
    def load_public_data_3(self, request):
        base_urls = [
            "https://api.odcloud.kr/api/15069220/v1/uddi:ca27bf6d-9bea-45c6-b96b-fd4ee98175f6",
            "https://api.odcloud.kr/api/15069220/v1/uddi:9fa3b979-9f4a-43a8-8990-d015794e963a",
            "https://api.odcloud.kr/api/15069220/v1/uddi:0834b568-9a1b-486c-bf02-bff412c5377b",
            "https://api.odcloud.kr/api/15069220/v1/uddi:87421b93-ed80-4719-ae49-d7a0c96a6991"
        ]
        service_key = NATION_DATA_KEY_3
        per_page = 100
        page = 1

        saved = []
        failed = []

        for base_url in base_urls:
        # 전체 페이지 수를 먼저 요청해서 가져옴
            count_url = f"{base_url}?page=1&perPage=1&returnType=json&serviceKey={service_key}"
            count_response = requests.get(count_url)
            if count_response.status_code != 200:
                return custom_response(data=None, code=400, message="요청 실패 (페이지 수 확인)", success=False)
            
            total_count = count_response.json().get("totalCount", 0)
            total_pages = (total_count // per_page) + (1 if total_count % per_page else 0)

            for page in range(1, total_pages + 1):
                url = f"{base_url}?page={page}&perPage={per_page}&returnType=json&serviceKey={service_key}"
                response = requests.get(url)

                if response.status_code != 200:
                    failed.append({"page": page, "reason": "해당 페이지 요청 실패"})
                    continue

                raw_data = response.json().get("data", [])

                for idx, item in enumerate(raw_data, start=1):
                    try:
                        # '베트남' 항목만 저장
                        사업대상지 = item.get("사업대상지", "")
                        if not 사업대상지:
                            continue  # 값이 비어 있으면 건너뜀

                        matched_nation = None
                        for nation in Nation.objects.all():
                            if nation.nation_name and nation.nation_name in 사업대상지:
                                matched_nation = nation
                                break

                        if not matched_nation:
                            continue  # Nation과 일치하는 나라가 없으면 건너뜀

                        # 지원분야 → exchange_category 변환
                        field = item.get("지원분야", "")

                        if any(keyword in field for keyword in health_keywords):
                            category = "health"
                        elif any(keyword in field for keyword in edu_keywords):
                            category = "edu"
                        elif any(keyword in field for keyword in culture_keywords):
                            category = "culture"
                        elif any(keyword in field for keyword in system_keywords):
                            category = "system"
                        else:
                            category = "etc"

                        nation_name_field = item.get("사업대상지", "")
                        if "베트남" in nation_name_field:
                            nation_name = "베트남"
                        else:
                            nation_name = nation_name_field.split()[0] if nation_name_field else None

                        if not nation_name:
                            failed.append({"index": idx, "reason": "국가명 없음", "item": item})
                            continue

                        nation = Nation.objects.filter(nation_name__icontains=nation_name).first()
                        if not nation:
                            failed.append({"index": idx, "reason": f"Nation 객체 없음 (nation_name: {nation_name})", "item": item})
                            continue

                        exchange_name_kr = item.get("사업명(국문)")
                        if not exchange_name_kr:
                            failed.append({"index": idx, "reason": "사업명(국문) 없음", "item": item})
                            continue

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
                        saved.append({"page": page, "index": idx, "id": obj.exchange_id, "created": created})

                    except Exception as e:
                        failed.append({"page": page, "index": idx, "reason": str(e), "item": item})

        return custom_response(
            data={
                "saved_count": len(saved),
                "failed_count": len(failed),
                "saved": saved,
                "failed": failed,
                "message": "전체 페이지 데이터 저장 완료"
            },
            code=200,
            message="완료"
        )

    @action(detail=False, methods=['post'])
    def load_public_data_4(self, request):
        base_url = "https://api.odcloud.kr/api/15113634/v1/uddi:4b3bea0d-510b-4d18-9cdf-837aaf5162d8"
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
                    nation_name = item.get("아프리카 국가")
                    if not nation_name:
                        failed.append({"page": page, "index": idx, "reason": "국가명 없음", "item": item})
                        continue

                    nation = next((n for n in nations if n.nation_name in nation_name), None)
                    if not nation:
                        failed.append({"page": page, "index": idx, "reason": f"Nation 객체 없음 ({nation_name})", "item": item})
                        continue

                    year = item.get("교류연도")
                    exchange_name_kr = f"{item.get('기초지자체', '')}_{item.get('아프리카 국가', '')} 교류"
                    exchange_content = item.get("주요내용")

                    # 유형 분류
                    field = item.get("교류유형", "")
                    if any(keyword in field for keyword in health_keywords):
                        category = "health"
                    elif any(keyword in field for keyword in edu_keywords):
                        category = "edu"
                    elif any(keyword in field for keyword in culture_keywords):
                        category = "culture"
                    elif any(keyword in field for keyword in system_keywords):
                        category = "system"
                    else:
                        category = "etc"
                    others = f"""
                        광역시도: {item.get('광역시도', '')}
                        기초지자체: {item.get('기초지자체', '')}
                        아프리카 지자체: {item.get('아프리카 지자체', '')}
                        교류유형: {item.get('교류유형', '')}
                    """

                    obj, created = ExchangeData.objects.update_or_create(
                        exchange_name_kr=exchange_name_kr,
                        exchange_nation=nation,
                        exchange_category = category,
                        exchange_content = exchange_content,
                        start_year = year,
                        end_year = year,
                        others = others,
                        defaults={
                            "exchange_name_en": None,
                            "pub_date": date.today()
                        }
                    )

                    saved.append({"base_url": base_url, "page": page, "index": idx, "id": obj.exchange_id, "created": created})

                except Exception as e:
                    failed.append({"base_url": base_url, "page": page, "index": idx, "reason": str(e), "item": item})

        return custom_response(
            data={
                "saved_count": len(saved),
                "failed_count": len(failed),
                "saved": saved,
                "failed": failed,
                "message": "전체 페이지 데이터 저장 완료"
            },
            code=200,
            message="완료"
        )
    
    @action(detail=False, methods=['post'])
    def load_public_data_1(self, request):

        base_url = "http://apis.data.go.kr/B260004/PublicDiplomacyBusinessInfoService/getPublicDiplomacyBusinessInfoList"
        service_key = NATION_DATA_KEY_3
        per_page = 100
        page = 1

        saved = []
        failed = []

        nations = list(Nation.objects.all())
        
        count_url = f"{base_url}?numOfRows=1&pageNo=1&returnType=json&serviceKey={service_key}"

        count_response = requests.get(count_url)
        if count_response.status_code != 200:
            return custom_response(data=None, code=400, message="페이지 수 확인 실패", success=False)

        body_data = count_response.json().get("response", {}).get("body", {})
        total_count = body_data.get("totalCount", 0)
        total_pages = (total_count // per_page) + (1 if total_count % per_page else 0)

        for page in range(1, total_pages + 1):
            url = f"{base_url}?pageNo={page}&numOfRows={per_page}&returnType=json&serviceKey={service_key}"
            response = requests.get(url)

            if response.status_code != 200:
                failed.append({"base_url": base_url, "page": page, "reason": "요청 실패"})
                continue

            items = response.json().get("response", {}).get("body", {}).get("items", {}).get("item", [])

            for idx, item in enumerate(items, start=1):
                try:
                    nation_name = item.get("country_nm")
                    kor_name = item.get("kor_business_nm")

                    if not nation_name and not kor_name:
                        failed.append({"page": page, "index": idx, "reason": "국가명 및 사업명 없음", "item": item})
                        continue

                    # nation 찾기 (country_nm 우선, 없으면 kor_business_nm 확인)
                    nation = None
                    if nation_name:
                        nation = next((n for n in nations if n.nation_name in nation_name), None)
                    if not nation and kor_name:
                        nation = next((n for n in nations if n.nation_name in kor_name), None)

                    if not nation:
                        failed.append({
                            "page": page,
                            "index": idx,
                            "reason": f"Nation 객체 없음 (country_nm: {nation_name}, kor_business_nm: {kor_name})",
                            "item": item
                        })
                        continue

                    if not kor_name:
                        failed.append({"page": page, "index": idx, "reason": "사업명 없음", "item": item})
                        continue

                    # 다년 여부 및 연도 설정
                    business_year = item.get("business_year")
                    multi_type = item.get("multi_year_type", "")
                    start_year = end_year = business_year

                    if multi_type == "다년" and kor_name:
                        match = re.search(r"(\d{4})[^\d]?[-~][^\d]?(\d{2,4})", kor_name)
                        if match:
                            start_year = int(match.group(1))
                            end_raw = match.group(2)
                            if len(end_raw) == 2:
                                end_year = int(str(start_year)[:2] + end_raw)
                            else:
                                end_year = int(end_raw)

                    # 유형 분류
                    detail = item.get("detail_business", "")
                    if any(keyword in detail for keyword in health_keywords):
                        category = "health"
                    elif any(keyword in detail for keyword in edu_keywords):
                        category = "edu"
                    elif any(keyword in detail for keyword in culture_keywords):
                        category = "culture"
                    elif any(keyword in detail for keyword in system_keywords):
                        category = "system"
                    else:
                        category = "etc"

                    others = f"""
                        목적: {item.get('business_purpose', '')}
                        단위사업: {item.get('unit_business', '')}
                        상세분류: {item.get('detail_business', '')}
                        대상: {item.get('business_target', '')}
                        다년여부: {item.get('multi_year_type', '')}
                    """

                    obj, created = ExchangeData.objects.update_or_create(
                        exchange_name_kr=kor_name,
                        exchange_nation=nation,
                        exchange_category = category,
                        start_year = start_year,
                        end_year = end_year,
                        others = others,
                        defaults={
                            "exchange_name_en": item.get("eng_business_nm"),
                            "exchange_content": item.get("business_purpose"),
                            "pub_date": date.today()
                        }
                    )

                    saved.append({"base_url": base_url, "page": page, "index": idx, "id": obj.exchange_id, "created": created})

                except Exception as e:
                    failed.append({"base_url": base_url, "page": page, "index": idx, "reason": str(e), "item": item})

        return custom_response(
            data={
                "saved_count": len(saved),
                "failed_count": len(failed),
                "saved": saved,
                "failed": failed,
                "message": "전체 페이지 데이터 저장 완료"
            },
            code=200,
            message="완료"
        )

class LocalDataAPI(viewsets.ViewSet):

    @action(detail=False, methods=['post'])
    def load_seoul_sister_data(self, request):
        base_url = "http://openAPI.seoul.go.kr:8088"
        service_key = SEOUL_API_KEY

        count_url = f"{base_url}/{service_key}/json/ListSysterCityInfo/1/1"

        try:
            response = requests.get(count_url)
            data = response.json()

            total_count = data.get("ListSysterCityInfo", {}).get("list_total_count", None)

            url = f"{base_url}/{service_key}/json/ListSysterCityInfo/1/{total_count}"

            try:
                response = requests.get(url)
                data = response.json()
                rows = data.get("ListSysterCityInfo", {}).get("row", [])

                origin_city = LocalGoverment.objects.get(local_name="서울특별시")

                saved_count = 0
                skipped = []

                for item in rows:
                    nation = item.get("NATIONNAME", "").strip()
                    city = item.get("CITYNAME", "").strip()
                    date_str = item.get("AGREE_DATE", "").strip()

                    if city == "기타":
                        skipped.append(f"{nation} - 기타 (생성 안 함)")
                        continue

                    # 날짜 파싱
                    try:
                        agreement_date = datetime.strptime(date_str, "%Y%m%d").date()
                    except ValueError:
                        continue  # 날짜 형식 이상하면 스킵

                    # 중복 체크
                    if LocalData.objects.filter(
                        origin_city=origin_city,
                        partner_country=nation,
                        partner_city=city
                    ).exists():
                        skipped.append(f"{nation} - {city}")
                        continue

                    LocalData.objects.create(
                        origin_city=origin_city,
                        partner_country=nation,
                        partner_city=city,
                        category='sister',
                        agreement_date=agreement_date
                    )
                    saved_count += 1

                return custom_response(
                    data={
                        "saved": saved_count,
                        "skipped": skipped
                    },
                    message="서울특별시 자매도시 저장 완료"
                )

            except Exception as e:
                return custom_response(message=str(e), code=status.HTTP_500_INTERNAL_SERVER_ERROR, success=False)
        except Exception as e:
            return custom_response(message=str(e), code=status.HTTP_500_INTERNAL_SERVER_ERROR, success=False)
        
    @action(detail=False, methods=['post'])
    def load_seoul_friendly_data(self, request):
        base_url = "http://openAPI.seoul.go.kr:8088"
        service_key = SEOUL_API_KEY

        count_url = f"{base_url}/{service_key}/json/ListFriendCityInfo/1/1"

        try:
            response = requests.get(count_url)
            data = response.json()

            total_count = data.get("ListFriendCityInfo", {}).get("list_total_count", None)

            url = f"{base_url}/{service_key}/json/ListFriendCityInfo/1/{total_count}"

            try:
                response = requests.get(url)
                data = response.json()
                rows = data.get("ListFriendCityInfo", {}).get("row", [])

                origin_city = LocalGoverment.objects.get(local_name="서울특별시")

                saved_count = 0
                skipped = []

                for item in rows:
                    nation = item.get("NATIONNAME", "").strip()
                    city = item.get("CITYNAME", "").strip()
                    date_str = item.get("AGREE_DATE", "").strip()

                    # 날짜 파싱
                    try:
                        agreement_date = datetime.strptime(date_str, "%Y%m%d").date()
                    except ValueError:
                        continue  # 날짜 형식 이상하면 스킵

                    # 중복 체크
                    if LocalData.objects.filter(
                        origin_city=origin_city,
                        partner_country=nation,
                        partner_city=city
                    ).exists():
                        skipped.append(f"{nation} - {city}")
                        continue

                    LocalData.objects.create(
                        origin_city=origin_city,
                        partner_country=nation,
                        partner_city=city,
                        category='friendly',
                        agreement_date=agreement_date
                    )
                    saved_count += 1

                return custom_response(
                    data={
                        "saved": saved_count,
                        "skipped": skipped
                    },
                    message="서울특별시 우호결연 도시 저장 완료"
                )

            except Exception as e:
                return custom_response(message=str(e), code=status.HTTP_500_INTERNAL_SERVER_ERROR, success=False)
        except Exception as e:
            return custom_response(message=str(e), code=status.HTTP_500_INTERNAL_SERVER_ERROR, success=False)

    @action(detail=False, methods=['post'])
    def load_pusan_sister_data(self, request):
        base_url = "https://api.odcloud.kr/api/15088427/v1/uddi:ff70b662-de23-432d-9708-b2c314ba5eb7"
        service_key = NATION_DATA_KEY_3
        per_page = 10
        page = 1

        saved = []
        failed = []

        count_url = f"{base_url}?page=1&perPage=1&returnType=json&serviceKey={service_key}"
        count_response = requests.get(count_url)
        if count_response.status_code != 200:
            return custom_response(data=None, code=400, message="페이지 수 확인 실패", success=False)

        total_count = count_response.json().get("totalCount", 0)
        total_pages = (total_count // per_page) + (1 if total_count % per_page else 0)

        try:
            origin_city = LocalGoverment.objects.get(local_name="부산광역시")
        except LocalGoverment.DoesNotExist:
            return custom_response(data=None, code=404, message="부산광역시 LocalGoverment 데이터가 없습니다.", success=False)

        for page in range(1, total_pages + 1):
            url = f"{base_url}?page={page}&perPage={per_page}&returnType=json&serviceKey={service_key}"
            response = requests.get(url)

            if response.status_code != 200:
                failed.append({"page": page, "reason": "요청 실패"})
                continue

            raw_data = response.json().get("data", [])

            for item in raw_data:
                nation = item.get("국가명", "").strip()
                city = item.get("도시명", "").strip()
                date_str = item.get("결연일자", "").strip()

                # 도시명 또는 날짜 없으면 스킵
                if not city or not date_str:
                    failed.append({"nation": nation, "city": city, "reason": "도시명 또는 날짜 없음"})
                    continue

                korean_city = extract_korean_only(city)
                if not korean_city:
                    failed.append({"nation": nation, "city": city, "reason": "한글 없음"})
                    continue

                # 날짜 파싱
                try:
                    agreement_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                except ValueError:
                    failed.append({"nation": nation, "city": city, "reason": f"날짜 형식 오류: {date_str}"})
                    continue

                # 중복 체크 (같은 origin_city, nation, city, date가 있으면 건너뜀)
                if LocalData.objects.filter(
                    origin_city=origin_city,
                    partner_country=nation,
                    partner_city=korean_city,
                    agreement_date=agreement_date
                ).exists():
                    continue

                try:
                    LocalData.objects.create(
                        origin_city=origin_city,
                        partner_country=nation,
                        partner_city=korean_city,
                        category="sister",
                        agreement_date=agreement_date
                    )
                    saved.append(f"{nation} - {city}")
                except Exception as e:
                    failed.append({"nation": nation, "city": city, "reason": str(e)})

        return custom_response(
            data={
                "saved_count": len(saved),
                "saved": saved,
                "failed_count": len(failed),
                "failed": failed
            },
            message="부산광역시 자매도시 데이터 처리 결과"
        )
    
    @action(detail=False, methods=['post'])
    def load_pusan_friendly_data(self, request):
        base_url = "https://api.odcloud.kr/api/15088426/v1/uddi:47d7e024-7dc7-4166-898c-c4c3fc9f303c"
        service_key = NATION_DATA_KEY_3
        per_page = 10
        page = 1

        saved = []
        failed = []

        count_url = f"{base_url}?page=1&perPage=1&returnType=json&serviceKey={service_key}"
        count_response = requests.get(count_url)
        if count_response.status_code != 200:
            return custom_response(data=None, code=400, message="페이지 수 확인 실패", success=False)

        total_count = count_response.json().get("totalCount", 0)
        total_pages = (total_count // per_page) + (1 if total_count % per_page else 0)

        try:
            origin_city = LocalGoverment.objects.get(local_name="부산광역시")
        except LocalGoverment.DoesNotExist:
            return custom_response(data=None, code=404, message="부산광역시 LocalGoverment 데이터가 없습니다.", success=False)

        for page in range(1, total_pages + 1):
            url = f"{base_url}?page={page}&perPage={per_page}&returnType=json&serviceKey={service_key}"
            response = requests.get(url)

            if response.status_code != 200:
                failed.append({"page": page, "reason": "요청 실패"})
                continue

            raw_data = response.json().get("data", [])

            for item in raw_data:
                nation = item.get("국가명", "").strip()
                city = item.get("도시명", "").strip()
                date_str = item.get("결연일자", "").strip()

                # 도시명 또는 날짜 없으면 스킵
                if not city or not date_str:
                    failed.append({"nation": nation, "city": city, "reason": "도시명 또는 날짜 없음"})
                    continue

                korean_city = extract_korean_only(city)
                if not korean_city:
                    failed.append({"nation": nation, "city": city, "reason": "한글 없음"})
                    continue

                # 날짜 파싱
                try:
                    agreement_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                except ValueError:
                    failed.append({"nation": nation, "city": city, "reason": f"날짜 형식 오류: {date_str}"})
                    continue

                # 중복 체크 (같은 origin_city, nation, city, date가 있으면 건너뜀)
                if LocalData.objects.filter(
                    origin_city=origin_city,
                    partner_country=nation,
                    partner_city=korean_city,
                    agreement_date=agreement_date
                ).exists():
                    continue

                try:
                    LocalData.objects.create(
                        origin_city=origin_city,
                        partner_country=nation,
                        partner_city=korean_city,
                        category="friendly",
                        agreement_date=agreement_date
                    )
                    saved.append(f"{nation} - {city}")
                except Exception as e:
                    failed.append({"nation": nation, "city": city, "reason": str(e)})

        return custom_response(
            data={
                "saved_count": len(saved),
                "saved": saved,
                "failed_count": len(failed),
                "failed": failed
            },
            message="부산광역시 우호결연 도시 데이터 처리 결과"
        )
    
    # 인천 자매도시 우호도시 구분 안 되어 있음!!ㅡ.ㅡ
    @action(detail=False, methods=['post'])
    def load_incheon_sister_data(self, request):
        base_url = "https://api.odcloud.kr/api/15104012/v1/uddi:8e6b5c31-f912-429c-bb73-a4be605fbdd5"
        service_key = NATION_DATA_KEY_3
        per_page = 10
        page = 1

        saved = []
        failed = []

        count_url = f"{base_url}?page=1&perPage=1&returnType=json&serviceKey={service_key}"
        count_response = requests.get(count_url)
        if count_response.status_code != 200:
            return custom_response(data=None, code=400, message="페이지 수 확인 실패", success=False)

        total_count = count_response.json().get("totalCount", 0)
        total_pages = (total_count // per_page) + (1 if total_count % per_page else 0)

        try:
            origin_city = LocalGoverment.objects.get(local_name="인천광역시")
        except LocalGoverment.DoesNotExist:
            return custom_response(data=None, code=404, message="인천광역시 LocalGoverment 데이터가 없습니다.", success=False)

        for page in range(1, total_pages + 1):
            url = f"{base_url}?page={page}&perPage={per_page}&returnType=json&serviceKey={service_key}"
            response = requests.get(url)

            if response.status_code != 200:
                failed.append({"page": page, "reason": "요청 실패"})
                continue

            raw_data = response.json().get("data", [])

            for item in raw_data:
                nation = item.get("국 가", "").strip()
                city = item.get("도 시", "").strip()
                date_str = item.get("결연일", "").strip()

                # 도시명 또는 날짜 없으면 스킵
                if not city or not date_str:
                    failed.append({"nation": nation, "city": city, "reason": "도시명 또는 날짜 없음"})
                    continue

                korean_city = extract_korean_only(city)
                if not korean_city:
                    failed.append({"nation": nation, "city": city, "reason": "한글 없음"})
                    continue

                # 날짜 파싱
                try:
                    agreement_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                except ValueError:
                    failed.append({"nation": nation, "city": city, "reason": f"날짜 형식 오류: {date_str}"})
                    continue

                # 중복 체크 (같은 origin_city, nation, city, date가 있으면 건너뜀)
                if LocalData.objects.filter(
                    origin_city=origin_city,
                    partner_country=nation,
                    partner_city=korean_city,
                    agreement_date=agreement_date
                ).exists():
                    continue

                try:
                    LocalData.objects.create(
                        origin_city=origin_city,
                        partner_country=nation,
                        partner_city=korean_city,
                        category="sister",
                        agreement_date=agreement_date
                    )
                    saved.append(f"{nation} - {city}")
                except Exception as e:
                    failed.append({"nation": nation, "city": city, "reason": str(e)})

        return custom_response(
            data={
                "saved_count": len(saved),
                "saved": saved,
                "failed_count": len(failed),
                "failed": failed
            },
            message="인천광역시 자매도시 데이터 처리 결과"
        )
    
    @action(detail=False, methods=['post'])
    def load_jeju_local_data(self, request):
        base_url = "https://api.odcloud.kr/api/15018494/v1/uddi:17a1fc98-a237-4527-8496-e7398a9ac890"
        service_key = NATION_DATA_KEY_3
        per_page = 10
        page = 1

        saved = []
        failed = []

        count_url = f"{base_url}?page=1&perPage=1&returnType=json&serviceKey={service_key}"
        count_response = requests.get(count_url)
        if count_response.status_code != 200:
            return custom_response(data=None, code=400, message="페이지 수 확인 실패", success=False)

        total_count = count_response.json().get("totalCount", 0)
        total_pages = (total_count // per_page) + (1 if total_count % per_page else 0)

        try:
            origin_city = LocalGoverment.objects.get(local_name="제주특별자치도")
        except LocalGoverment.DoesNotExist:
            return custom_response(data=None, code=404, message="제주특별자치도 LocalGoverment 데이터가 없습니다.", success=False)

        for page in range(1, total_pages + 1):
            url = f"{base_url}?page={page}&perPage={per_page}&returnType=json&serviceKey={service_key}"
            response = requests.get(url)

            if response.status_code != 200:
                failed.append({"page": page, "reason": "요청 실패"})
                continue

            raw_data = response.json().get("data", [])

            for item in raw_data:
                nation = item.get("국가", "").strip()
                city = item.get("도시명", "").strip()
                date_str = item.get("결연일자", "").strip()
                category = item.get("구분", "").strip()

                # 도시명 또는 날짜 없으면 스킵
                if not city or not date_str:
                    failed.append({"nation": nation, "city": city, "reason": "도시명 또는 날짜 없음"})
                    continue

                korean_city = extract_korean_only(city)
                if not korean_city:
                    failed.append({"nation": nation, "city": city, "reason": "한글 없음"})
                    continue

                # 날짜 파싱
                try:
                    agreement_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                except ValueError:
                    failed.append({"nation": nation, "city": city, "reason": f"날짜 형식 오류: {date_str}"})
                    continue

                # 중복 체크 (같은 origin_city, nation, city, date가 있으면 건너뜀)
                if LocalData.objects.filter(
                    origin_city=origin_city,
                    partner_country=nation,
                    category = category,
                    partner_city=korean_city,
                    agreement_date=agreement_date
                ).exists():
                    continue
                
                if category == "자매결연":
                    category = "sister"
                elif category == "우호도시":
                    category = "friendly"
                else:
                    failed.append({"nation": nation, "city": city, "reason": f"구분 오류: {category}"})
                    continue

                try:
                    LocalData.objects.create(
                        origin_city=origin_city,
                        partner_country=nation,
                        partner_city=korean_city,
                        category=category,
                        agreement_date=agreement_date
                    )
                    saved.append(f"{nation} - {city}")
                except Exception as e:
                    failed.append({"nation": nation, "city": city, "reason": str(e)})

        return custom_response(
            data={
                "saved_count": len(saved),
                "saved": saved,
                "failed_count": len(failed),
                "failed": failed
            },
            message="제주특별자치도 자매도시 데이터 처리 결과"
        )