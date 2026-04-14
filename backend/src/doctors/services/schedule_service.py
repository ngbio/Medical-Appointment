from datetime import datetime, date as dt_date
from rest_framework.exceptions import ValidationError

from doctors.models import DoctorSchedule, TimeSlot, SlotStatus
from users.models import RoleEnum

def parse_date(date_str):
    if not date_str:
        return dt_date.today()

    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise ValidationError({"date": "Invalid format. Use YYYY-MM-DD"})

# Get schedule from current doctor
def get_doctor_schedules(user, date_str=None):
    if user.role != RoleEnum.DOCTOR:
        raise ValidationError("Only doctors can access this.")

    work_date = parse_date(date_str)

    return DoctorSchedule.objects.filter(
        doctor__user=user,
        work_date=work_date
    )

# patient gets doctor schedule by date
def get_schedules_by_doctor(doctor_id, date_str=None):
    # Bắt đầu với query lấy theo bác sĩ
    queryset = DoctorSchedule.objects.filter(doctor_id=doctor_id)

    if date_str:
        queryset = queryset.filter(work_date=date_str)
    
    return queryset.order_by('work_date')


# available timeslots
def get_available_slots(schedule_id):
    if not schedule_id:
        raise ValidationError("schedule_id is required.")

    return TimeSlot.objects.filter(
        schedule_id=schedule_id,
        status=SlotStatus.AVAILABLE
    ).order_by("start_time")