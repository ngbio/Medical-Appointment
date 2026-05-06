from rest_framework import serializers
from django.db import transaction
from django.utils import timezone
from appointments.models import Appointment, AppointmentStatus
from appointments.tasks import send_appointment_confirmation, send_appointment_reminder
from doctors.models import SlotStatus, TimeSlot # Thêm TimeSlot vào đây

class AppointmentSerializer(serializers.ModelSerializer):
    doctor_name = serializers.CharField(source='doctor.user.fullname', read_only=True)
    patient_name = serializers.CharField(source='patient.user.fullname', read_only=True)
    appointment_date = serializers.DateField(source='time_slot.schedule.work_date', read_only=True)
    start_time = serializers.TimeField(source='time_slot.start_time', read_only=True)

    class Meta:
        model = Appointment
        fields = [
            'id', 'patient', 'patient_name', 'doctor', 'doctor_name',
            'time_slot', 'appointment_date', 'start_time',
            'symptoms', 'status', 'created_at', 'notes'
        ]
        read_only_fields = [
            'patient', 'doctor', 'status', 'created_at',
            'doctor_name', 'patient_name', 'appointment_date', 'start_time'
        ]

    def validate(self, attrs):
        time_slot = attrs.get('time_slot')
        today = timezone.localdate()

        if not time_slot:
            raise serializers.ValidationError({
                "time_slot": "Please select a time slot."
            })

        if time_slot.status != SlotStatus.AVAILABLE:
            raise serializers.ValidationError({
                "time_slot": "This time slot is already booked or unavailable."
            })

        if time_slot.schedule.work_date < today:
            raise serializers.ValidationError({
                "time_slot": "Cannot book an appointment in the past."
            })

        existing_active_appointment = Appointment.objects.filter(
            time_slot=time_slot,
            status__in=[AppointmentStatus.BOOKED, AppointmentStatus.COMPLETED]
        ).exists()

        if existing_active_appointment:
            raise serializers.ValidationError({
                "time_slot": "This time slot has already been booked by another appointment."
            })

        return attrs

    def create(self, validated_data):
        time_slot_instance = validated_data.get('time_slot')

        with transaction.atomic():
            time_slot = TimeSlot.objects.select_for_update().get(id=time_slot_instance.id)

            if time_slot.status != SlotStatus.AVAILABLE:
                raise serializers.ValidationError({
                    "time_slot": "This time slot was just booked by someone else."
                })

            validated_data['doctor'] = time_slot.schedule.doctor
            validated_data['status'] = AppointmentStatus.BOOKED
            validated_data['time_slot'] = time_slot

            appointment = super().create(validated_data)
            
            time_slot.status = SlotStatus.BOOKED
            time_slot.save(update_fields=['status'])

        # Send confirmation email asynchronously
        send_appointment_confirmation.delay(appointment.id)
        send_appointment_reminder.delay(appointment.id)

        return appointment