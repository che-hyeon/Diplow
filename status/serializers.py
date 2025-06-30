from rest_framework import serializers
from .models import Nation, LocalGoverment, NationDashboard, LocalDashboard, ExchangeData
from django.db.models import Count

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

class LocalDashboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocalDashboard
        fields = '__all__'

class ExchangeDataSerializer(serializers.ModelSerializer):
    exchange_nation = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = ExchangeData
        fields = '__all__'

    def get_exchange_nation(self, obj):
        return obj.exchange_nation.nation_name