from rest_framework import serializers
from .models import EnvironIssueData
from status.models import Nation

class EnvironIssueDataSerializer(serializers.ModelSerializer):
    nation_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = EnvironIssueData
        fields = [
            'environ_data_id',
            'nation',
            'nation_name',
            'environ_data_title',
            'pub_date'
        ]
    
    def get_nation_name(self, obj):
        return obj.nation.nation_name
    