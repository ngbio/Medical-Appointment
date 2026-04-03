from rest_framework.serializers import ModelSerializer
from rest_framework.exceptions import ValidationError
from ..models import DoctorSchedule, TimeSlot
from ..services.timeslot_service import generate_timeslots

class ScheduleSerializer(ModelSerializer):
    class Meta:
        model = DoctorSchedule
        fields = ['id', 'doctor', 'work_date', 'start_time', 'end_time']
        read_only_fields = ['id']
