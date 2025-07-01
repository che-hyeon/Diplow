from rest_framework import serializers
from .models import MovementData, DiplomacyEvent

class MovementDataKRSerializer(serializers.ModelSerializer):
    nation_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = MovementData
        fields = [
            'movement_data_id',
            'nation',
            'nation_name',
            'title_kr',
            'content_kr',
            'pub_date'
        ]
    
    def get_nation_name(self, obj):
        return obj.nation.nation_name
    
class DiplomacyEventSerializer(serializers.ModelSerializer):

    class Meta:
        model = DiplomacyEvent
        fields = [
            'event_id',
            'event_title',
            'event_category',
            'event_content',
            'url',
            'created_at'
        ]