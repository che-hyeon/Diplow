from rest_framework import serializers
from .models import Nation, LocalGoverment, NationDashboard, LocalDashboard, ExchangeData, LocalData, ExchangeCategory, Vision
from django.db.models import Count
from collections import defaultdict, Counter

class NationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nation
        fields = '__all__'

    # nation_image = serializers.ImageField(use_url=True, required=False)

class LocalGovermentSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocalGoverment
        fields = '__all__'

    # local_image = serializers.ImageField(use_url=True, required=False)

# nation map
class NationDashboardMapSerializer(serializers.ModelSerializer):
    nation_name = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = NationDashboard
        fields = ['nation_dash_id', 'nation', 'nation_name', 'nation_map_explain']
    
    def get_nation_name(self, obj):
        return obj.nation.nation_name

# category-ratio
class NationDashboardCategorySerializer(serializers.ModelSerializer):
    nation_name = serializers.SerializerMethodField(read_only=True)
    category_ratio = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = NationDashboard
        fields = [
            'nation_dash_id',
            'nation',
            'nation_name',
            'nation_ratio_explain',
            'nation_ratio_explain_detail',
            'category_ratio'
        ]
    
    def get_nation_name(self, obj):
        return obj.nation.nation_name
    
    def get_category_ratio(self, obj):
        nation= obj.nation

        exchanges = ExchangeData.objects.filter(exchange_nation=nation)

        category_counts = exchanges.values('exchange_category').annotate(count=Count('exchange_id'))
        total = exchanges.count() or 1  # 0으로 나누기 방지용

        ratio = {
            "health": 0,
            "edu": 0,
            "culture": 0,
            "system": 0,
        }

        for item in category_counts:
            cat = item['exchange_category']
            cnt = item['count']
            if cat in ratio:
                ratio[cat] = round((cnt / total) * 100, 2)  # % 소수점 2자리

        return ratio

# recent
class NationDashboardRecentSerializer(serializers.ModelSerializer):
    nation_name = serializers.SerializerMethodField(read_only=True)
    example = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = NationDashboard
        fields = [
            'nation_dash_id',
            'nation',
            'nation_name',
            'nation_recent_explain',
            'example'
        ]
    
    def get_nation_name(self, obj):
        return obj.nation.nation_name
    
    def get_example(self, obj):
        recent_exchanges = ExchangeData.objects.filter(
            exchange_nation=obj.nation
        ).order_by('-pub_date')[:3]

        return ExchangeDataSerializer(recent_exchanges, many=True, context=self.context).data

# year
class NationDashboardYearSerializer(serializers.ModelSerializer):
    yearly_data_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = NationDashboard
        fields = [
            'nation_dash_id',
            'nation',
            'nation_name',
            'nation_num_tend',
            'yearly_data_count'
        ]
    
    def get_yearly_data_count(self, obj):
        # 해당 나라와 연결된 ExchangeData 가져오기
        exchanges = ExchangeData.objects.filter(exchange_nation=obj.nation)

        # defaultdict으로 연도별 카운트 초기화
        year_count = defaultdict(int)

        for exchange in exchanges:
            start = exchange.start_year
            end = exchange.end_year or start  # 종료 연도가 없으면 시작 연도로 처리

            if start:
                for year in range(start, end + 1):
                    year_count[year] += 1

        # 정렬된 dict로 변환 (선택)
        return {str(year): year_count[year] for year in sorted(year_count)}

class LocalDashboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocalDashboard
        fields = '__all__'

# local map
class LocalDashboardMapSerializer(serializers.ModelSerializer):
    local_name = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = LocalDashboard
        fields = ['local_dash_id', 'local', 'local_name', 'local_map_explain']

    def get_local_name(self, obj):
        return obj.local.local_name
    
# local city: 자매도시 우호 도시 관련 api
class LocalDashboardCitySerializer(serializers.ModelSerializer):
    local_name = serializers.SerializerMethodField(read_only=True)
    sister_city = serializers.SerializerMethodField(read_only=True)
    friendship_city = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = LocalDashboard
        fields = [
            'local_dash_id',
            'local',
            'local_name',
            'sister_city',
            'friendship_city'
        ]
    
    def get_local_name(self, obj):
        return obj.local.local_name
    
    def get_sister_city(self, obj):
        localgov = obj.local

        sister_data = LocalData.objects.filter(
            origin_city=localgov,
            category='sister'
        )

        return {
            "explain": obj.local_sister_explain,
            "cities": [{"city": data.partner_city} for data in sister_data]
        }
    
    def get_friendship_city(self, obj):
        localgov = obj.local

        friendly_data = LocalData.objects.filter(
            origin_city=localgov,
            category='friendly'
        )

        return {
            "explain": obj.local_friendly_explain,
            "cities": [{"city": data.partner_city} for data in friendly_data]
        }

# 자매 우호결연 도시 보유국 순위
class LocalDashboardCityRankingSerializer(serializers.ModelSerializer):
    local_name = serializers.SerializerMethodField(read_only=True)
    city_ranking = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = LocalDashboard
        fields = [
            'local_dash_id',
            'local',
            'local_name',
            'local_ratio_explain',
            'local_ratio_explain_detail',
            'city_ranking'
        ]
    
    def get_local_name(self, obj):
        return obj.local.local_name
    
    def get_city_ranking(self, obj):
        localgov = obj.local

        local_data_qs = LocalData.objects.filter(origin_city=localgov)

        country_counter = Counter()
        for data in local_data_qs:
            if data.partner_country:
                country_counter[data.partner_country] += 1

        total = sum(country_counter.values())
        if total == 0:
            return []

        most_common = country_counter.most_common(4)
        other_total = total - sum([count for _, count in most_common])

        result = []
        for country_name, count in most_common:
            result.append({
                "nation_name": country_name,
                "percent": round(count / total * 100, 2)
            })

        if other_total > 0:
            result.append({
                "nation_name": "기타",
                "percent": round(other_total / total * 100, 2)
            })

        return result

# 주요 교류 분야
class LocalDashboardMajorSerializer(serializers.ModelSerializer):
    local_name = serializers.SerializerMethodField(read_only=True)
    major = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = LocalDashboard
        fields = [
            'local_dash_id',
            'local',
            'local_name',
            'local_category_explain',
            'major'
        ]
    
    def get_local_name(self, obj):
        return obj.local.local_name
    
    def get_major(self, obj):
        localgov = obj.local  # LocalGoverment 인스턴스

        categories = ExchangeCategory.objects.filter(local=localgov).order_by('-exchange_num')[:3]

        return [
            {
                "exchange_name": cat.exchange_name,
                "exchange_display": cat.get_exchange_name_display(),
                "exchange_num": cat.exchange_num
            }
            for cat in categories
        ]

# 지자체 주요 사업 영역
class LocalDashboardVisionSerializer(serializers.ModelSerializer):
    local_name = serializers.SerializerMethodField(read_only=True)
    projects = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = LocalDashboard
        fields = [
            'local_dash_id',
            'local',
            'local_name',
            'local_vision_explain',
            'projects'
        ]
    
    def get_local_name(self, obj):
        return obj.local.local_name
    
    def get_projects(self, obj):
        localgov = obj.local

        projects = Vision.objects.filter(local=localgov).order_by('-created_at')[:3]

        return [
            {
                "project_title": pro.vision_title,
                "project_category": pro.vision_category,
                "project_content": pro.vision_content,
                "project_created_at": pro.created_at
            }
            for pro in projects
        ]

class ExchangeDataSerializer(serializers.ModelSerializer):
    exchange_nation = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = ExchangeData
        fields = '__all__'

    def get_exchange_nation(self, obj):
        return obj.exchange_nation.nation_name
    
class LocalDataSerializer(serializers.ModelSerializer):
    origin_city = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = LocalData
        fields = '__all__'
    
    def get_origin_city(self, obj):
        return obj.origin_city.local_name
    
class ExchageCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = ExchangeCategory
        fields = '__all__'