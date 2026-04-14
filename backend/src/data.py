# -*- coding: utf-8 -*-
from datetime import date, time, datetime, timedelta
from django.contrib.auth import get_user_model
from users.models import RoleEnum, GenderEnum
from doctors.models import Specialty, DoctorProfile, DoctorSchedule, TimeSlot, SlotStatus
from appointments.models import Appointment, AppointmentStatus

User = get_user_model()

print("=== BẮT ĐẦU NẠP DỮ LIỆU ===")

# ==============================
# 1. DỌN DỮ LIỆU (AN TOÀN)
# ==============================
print("1. Đang dọn dẹp dữ liệu cũ...")

Appointment.objects.all().delete()
TimeSlot.objects.all().delete()
DoctorSchedule.objects.all().delete()
DoctorProfile.objects.all().delete()

User.objects.filter(
    username__in=['patient1', 'patient2', 'doctor1', 'doctor2', 'doctor3']
).delete()

Specialty.objects.all().delete()

# ==============================
# 2. CHUYÊN KHOA
# ==============================
print("2. Đang tạo Chuyên khoa...")

spec1, _ = Specialty.objects.get_or_create(name='Khoa Tim mạch')
spec2, _ = Specialty.objects.get_or_create(name='Khoa Da liễu')
spec3, _ = Specialty.objects.get_or_create(name='Khoa Thần kinh')

# ==============================
# 3. USERS + DOCTOR PROFILE
# ==============================
print("3. Đang tạo Users...")

p1_user, _ = User.objects.get_or_create(
    username='patient1',
    defaults=dict(password='123', role=RoleEnum.PATIENT, gender=GenderEnum.MALE, fullname='Bệnh nhân A', phone_number='0111')
)

p2_user, _ = User.objects.get_or_create(
    username='patient2',
    defaults=dict(password='123', role=RoleEnum.PATIENT, gender=GenderEnum.FEMALE, fullname='Bệnh nhân B', phone_number='0222')
)

d1_user, _ = User.objects.get_or_create(
    username='doctor1',
    defaults=dict(password='123', role=RoleEnum.DOCTOR, gender=GenderEnum.MALE, fullname='Bác sĩ Nguyễn Văn A', phone_number='0991')
)

d2_user, _ = User.objects.get_or_create(
    username='doctor2',
    defaults=dict(password='123', role=RoleEnum.DOCTOR, gender=GenderEnum.FEMALE, fullname='Bác sĩ Trần Thị B', phone_number='0992')
)

d3_user, _ = User.objects.get_or_create(
    username='doctor3',
    defaults=dict(password='123', role=RoleEnum.DOCTOR, gender=GenderEnum.MALE, fullname='Bác sĩ Lê Văn C', phone_number='0993')
)

d1_profile, _ = DoctorProfile.objects.get_or_create(user=d1_user, defaults={"specialty": spec1, "experience_years": 5})
d2_profile, _ = DoctorProfile.objects.get_or_create(user=d2_user, defaults={"specialty": spec2, "experience_years": 8})
d3_profile, _ = DoctorProfile.objects.get_or_create(user=d3_user, defaults={"specialty": spec3, "experience_years": 12})

# ==============================
# 4. SCHEDULE + TIMESLOTS
# ==============================
print("4. Đang tạo Schedule & TimeSlots...")

today = date.today()
doctors = [d1_profile, d2_profile, d3_profile]

all_slots = []

for doc in doctors:
    schedule, _ = DoctorSchedule.objects.get_or_create(
        doctor=doc,
        work_date=today,
        defaults=dict(start_time=time(8, 0), end_time=time(12, 0))
    )

    start_dt = datetime.combine(today, time(8, 0))

    for i in range(8):
        slot_start = (start_dt + timedelta(minutes=30*i)).time()
        slot_end = (start_dt + timedelta(minutes=30*(i+1))).time()

        # tránh trùng
        if not TimeSlot.objects.filter(
            schedule=schedule,
            start_time=slot_start,
            end_time=slot_end
        ).exists():
            all_slots.append(TimeSlot(
                schedule=schedule,
                start_time=slot_start,
                end_time=slot_end,
                status=SlotStatus.AVAILABLE
            ))

TimeSlot.objects.bulk_create(all_slots)

# ==============================
# 5. APPOINTMENTS
# ==============================
print("5. Đang tạo Appointments...")

patients = [p1_user.patient_profile, p2_user.patient_profile]
slots = list(TimeSlot.objects.filter(status=SlotStatus.AVAILABLE)[:10])

for i, slot in enumerate(slots):
    slot.status = SlotStatus.BOOKED
    slot.save()

    Appointment.objects.get_or_create(
        patient=patients[i % 2],
        doctor=slot.schedule.doctor,
        time_slot=slot,
        defaults=dict(
            status=AppointmentStatus.BOOKED,
            symptoms=f'Bệnh nhân đau đầu cấp độ {i+1}'
        )
    )

print("🎉 HOÀN TẤT! DATA ĐÃ SẴN SÀNG.")