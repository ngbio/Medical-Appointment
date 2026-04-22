from datetime import datetime, date as dt_date
from rest_framework.exceptions import ValidationError
from django.utils import timezone
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
    if not doctor_id:
        raise ValidationError("doctor_id is required.")
    
    today = timezone.localdate()
    
    # Bắt đầu với query lấy theo bác sĩ
    queryset = DoctorSchedule.objects.filter(doctor_id=doctor_id, work_date__gte=today)

    work_date = parse_date(date_str)

    if date_str:
        queryset = queryset.filter(work_date=work_date)
    
    return queryset.order_by('work_date')


# available timeslots
def get_available_slots(schedule_id):
    if not schedule_id:
        raise ValidationError("schedule_id is required.")
    
    now = timezone.localtime()
    today = now.date()
    current_time = now.time()

    queryset = TimeSlot.objects.filter(
        schedule_id=schedule_id,
        status=SlotStatus.AVAILABLE
    )

    schedule = DoctorSchedule.objects.get(id=schedule_id)

    if schedule.work_date == today:
        queryset = queryset.filter(start_time__gte=current_time)

    return queryset.order_by("start_time")