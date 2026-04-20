from django.db.models import F
from appointments.models import Appointment


def get_base_queryset():
    return Appointment.objects.select_related(
        'doctor__user',
        'patient__user',
        'time_slot__schedule'
    ).annotate(
        work_date=F('time_slot__schedule__work_date'),
        slot_time=F('time_slot__start_time')
    )