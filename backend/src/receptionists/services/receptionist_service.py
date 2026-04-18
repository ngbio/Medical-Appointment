from django.db import transaction
from rest_framework.exceptions import ValidationError
import random

from users.models import User, PatientProfile, RoleEnum
from doctors.models import TimeSlot, SlotStatus
from appointments.models import AppointmentStatus, Appointment
from appointments.serializers.appointment_serializers import AppointmentSerializer


def create_patient_and_appointment(
    phone: str,
    fullname: str,
    email: str,
    time_slot,
    symptoms: str,
    notes: str = ""
):
    with transaction.atomic():

        # Create or get user
        user, created = User.objects.get_or_create(
            username=phone,
            defaults={
                "phone_number": phone,
                "fullname": fullname,
                "email": email,
                "role": RoleEnum.PATIENT
            }
        )
        if created:
            password = str("123")
            user.set_password(password)
            user.save()

        # Ensure patient profile
        patient_profile, _ = PatientProfile.objects.get_or_create(user=user)

        slot = TimeSlot.objects.select_for_update().get(id=time_slot.id)

        if slot.status != SlotStatus.AVAILABLE:
            raise ValidationError({
                "time_slot": "This time slot is already booked."
            })

        # Create appointment
        appointment = Appointment.objects.create(
            patient=patient_profile,
            doctor=slot.schedule.doctor,
            time_slot=slot,
            symptoms=symptoms,
            notes=notes,
            status=AppointmentStatus.BOOKED
        )

        slot.status = SlotStatus.BOOKED
        slot.save(update_fields=["status"])

        return appointment, created