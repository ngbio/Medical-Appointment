from rest_framework.serializers import ModelSerializer
from ..models import TimeSlot


class TimeSlotSerializer(ModelSerializer):
    class Meta:
        model = TimeSlot
        fields = ['id', 'schedule', 'start_time', 'end_time', 'status']
        read_only_fields = ['id', 'schedule', 'start_time', 'end_time', 'status']