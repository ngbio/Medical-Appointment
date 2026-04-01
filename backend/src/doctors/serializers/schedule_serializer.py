from rest_framework.serializers import ModelSerializer
from rest_framework.exceptions import ValidationError
from ..models import DoctorSchedule, TimeSlot
from ..services.timeslot_service import generate_timeslots

class ScheduleSerializer(ModelSerializer):
    class Meta:
        model = DoctorSchedule
        fields = ['id', 'doctor', 'work_date', 'start_time', 'end_time']
        read_only_fields = ['id']

    def validate(self, data):
        if data['start_time'] >= data['end_time']:
            raise ValidationError("Start time must be before end time.")
        
        # Check for overlapping schedules
        overlapping_schedules = DoctorSchedule.objects.filter(
            doctor=data['doctor'],
            work_date=data['work_date'],
            start_time__lt=data['end_time'],
            end_time__gt=data['start_time']
        )
        if self.instance:
            overlapping_schedules = overlapping_schedules.exclude(id=self.instance.id)

        if overlapping_schedules.exists():
            raise ValidationError("This schedule overlaps with an existing schedule.")

        return data

    def create(self, validated_data):
        schedule = DoctorSchedule.objects.create(**validated_data)
        generate_timeslots(schedule=schedule)
        return schedule