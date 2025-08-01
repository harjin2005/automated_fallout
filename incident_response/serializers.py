from rest_framework import serializers
from .models import Incident, Action, Deliverable ,  AIAgentStatus

class DeliverableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deliverable
        fields = '__all__'

class ActionSerializer(serializers.ModelSerializer):
    deliverables = DeliverableSerializer(many=True, read_only=True)
    
    class Meta:
        model = Action
        fields = '__all__'

class IncidentSerializer(serializers.ModelSerializer):
    actions = ActionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Incident
        fields = '__all__'

class AIAgentStatusSerializer(serializers.ModelSerializer):
    duration = serializers.SerializerMethodField()
    incident_title = serializers.CharField(source='incident.title', read_only=True)
    
    class Meta:
        model = AIAgentStatus
        fields = '__all__'
    
    def get_duration(self, obj):
        if obj.completed_at and obj.started_at:
            delta = obj.completed_at - obj.started_at
            return int(delta.total_seconds())
        return None
