from django.db import transaction
from rest_framework.exceptions import ValidationError
import random

from users.models import User, PatientProfile, RoleEnum
from doctors.models import TimeSlot, SlotStatus
from appointments.models import AppointmentStatus, Appointment
from django.db import IntegrityError

def get_or_create_patient_user(phone, fullname, email):
    try:
        user = User.objects.filter(phone_number=phone).first()

        if user:
            return user, False

        user = User.objects.create(
            username=phone,
            phone_number=phone,
            fullname=fullname,
            email=email,
            role=RoleEnum.PATIENT
        )
        user.set_password("123")
        user.save()

        return user, True

    except IntegrityError:
        # handle race condition (2 request cùng lúc)
        user = User.objects.get(phone_number=phone)
        return user, False

def create_patient_and_appointment(
        phone: str,
        fullname: str,
        email: str,
        time_slot,
        symptoms: str,
        notes: str = ""
    ):
    with transaction.atomic():

        user, created = get_or_create_patient_user(phone, fullname, email)

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