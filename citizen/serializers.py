from rest_framework import serializers
from .models import Opinion, Program

class OpinionSerializer(serializers.ModelSerializer):
    local_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Opinion
        fields = [
            'opinion_id',
            'local',
            'local_name',
            'title',
            'content',
            'created_at'
        ]

    def get_local_name(self,obj):
        return obj.local.local_name
    
class ProgramSerializer(serializers.ModelSerializer):
    local_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Program
        fields = [
            'program_id',
            'local',
            'local_name',
            'program_name',
            'program_content',
            'url',
            'created_at'
        ]
    
    def get_local_name(self, obj):
        return obj.local.local_name