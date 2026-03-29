from rest_framework import serializers
import datetime
from .models import Appointment, AppointmentStatus
from doctors.models import SlotStatus


class AppointmentSerializer(serializers.ModelSerializer):
    doctor_name = serializers.CharField(source='doctor.user.get_full_name', read_only=True)
    patient_name = serializers.CharField(source='patient.user.get_full_name', read_only=True)
    appointment_date = serializers.DateField(source='time_slot.schedule.work_date', read_only=True)
    start_time = serializers.TimeField(source='time_slot.start_time', read_only=True)

    class Meta:
        model = Appointment
        fields = [
            'id', 'patient', 'patient_name', 'doctor', 'doctor_name',
            'time_slot', 'appointment_date', 'start_time',
            'symptoms', 'status', 'created_at'
        ]
        read_only_fields = [
            'patient', 'doctor', 'status', 'created_at',
            'doctor_name', 'patient_name', 'appointment_date', 'start_time'
        ]

    def validate(self, attrs):
        time_slot = attrs.get('time_slot')
        today = datetime.date.today()

        if not time_slot:
            raise serializers.ValidationError({
                "time_slot": "Vui lòng chọn khung giờ."
            })

        if time_slot.status != SlotStatus.AVAILABLE:
            raise serializers.ValidationError({
                "time_slot": "Khung giờ này đã được đặt hoặc không khả dụng."
            })

        if time_slot.schedule.work_date < today:
            raise serializers.ValidationError({
                "time_slot": "Bạn không thể đặt lịch khám cho ngày trong quá khứ."
            })

        return attrs

    def create(self, validated_data):
        time_slot = validated_data.get('time_slot')

        validated_data['doctor'] = time_slot.schedule.doctor
        validated_data['status'] = AppointmentStatus.BOOKED

        appointment = super().create(validated_data)

        time_slot.status = SlotStatus.BOOKED
        time_slot.save()

        return appointment