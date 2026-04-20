from rest_framework.serializers import ModelSerializer
from rest_framework.exceptions import ValidationError
from rest_framework import serializers
import re
import random

from doctors.models import TimeSlot, SlotStatus
from appointments.models import AppointmentStatus, Appointment
from users.models import User, PatientProfile, RoleEnum
from appointments.serializers.appointment_serializers import AppointmentSerializer
from ..services.receptionist_service import create_patient_and_appointment

class ReceptionistBookSerializer(ModelSerializer):
    # patient info
    phone_number = serializers.CharField()
    fullname = serializers.CharField()
    email = serializers.EmailField(required=False, allow_blank=True)

    # appointment info
    start_time = serializers.TimeField(source='time_slot.start_time', read_only=True)
    appointment_date = serializers.DateField(source='time_slot.schedule.work_date', read_only=True)
    doctor_name = serializers.CharField(source='doctor.user.fullname', read_only=True)
    time_slot = serializers.PrimaryKeyRelatedField(queryset=TimeSlot.objects.all())
    
    symptoms = serializers.CharField()
    notes = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Appointment
        fields = [
            "id", "phone_number", "fullname", "email",
            "time_slot", "symptoms", "notes",
            "appointment_date", "start_time", "doctor_name",
            "status"
        ]
        read_only_fields = ["id", "status", "appointment_date", "start_time", "doctor_name"]


    def validate_phone_number(self, value):
        if not re.match(r'^\d{10,11}$', value):
            raise serializers.ValidationError("Invalid phone number")
        return value
    def validate(self, attrs):
        phone = attrs.get("phone_number")

        existing_user = User.objects.filter(phone_number=phone).first()

        if existing_user:
            pass

        return attrs
    
    def create(self, validated_data):
        phone = validated_data.pop("phone_number")
        fullname = validated_data.pop("fullname")
        email = validated_data.pop("email", "")

        appointment, _ = create_patient_and_appointment(
            phone=phone,
            fullname=fullname,
            email=email,
            time_slot=validated_data["time_slot"],
            symptoms=validated_data["symptoms"],
            notes=validated_data.get("notes", "")
        )

        return appointment
