"""
Script to complete and enhance data initialization for Medical Appointment System
Tạo thêm dữ liệu còn thiếu:
- Receptionist users
- Admin user  
- Notifications cho appointments
- Multiple schedules cho nhiều ngày
- PatientProfile details (address, dob)
"""

import os
import django
from datetime import date, time, datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings')
django.setup()

from django.contrib.auth import get_user_model
from users.models import RoleEnum, GenderEnum, PatientProfile
from doctors.models import Specialty, DoctorProfile, DoctorSchedule, TimeSlot, SlotStatus
from appointments.models import Appointment, AppointmentStatus
from notifications.models import Notification, NotificationStatus

User = get_user_model()

print("=" * 50)
print("🔧 BẮT ĐẦU HOÀN THIỆN DỮ LIỆU")
print("=" * 50)

# ==============================
# 1. CREATE RECEPTIONIST USERS
# ==============================
print("\n1️⃣  Tạo Receptionist users...")

receptionist_data = [
    ("receptionist1", "123", "Lễ Tân A", "0881001"),
    ("receptionist2", "123", "Lễ Tân B", "0882002"),
]

receptionist_users = []
for username, password, fullname, phone in receptionist_data:
    user, created = User.objects.get_or_create(
        username=username,
        defaults=dict(
            role=RoleEnum.RECEPTIONIST,
            gender=GenderEnum.FEMALE,
            fullname=fullname,
            phone_number=phone
        )
    )
    
    if created:
        user.set_password(password)
        user.save()
        print(f"   ✅ Tạo receptionist: {username} ({fullname})")
    else:
        print(f"   ⏭️  Receptionist đã tồn tại: {username}")
    
    receptionist_users.append(user)

# ==============================
# 2. CREATE ADMIN USER
# ==============================
print("\n2️⃣  Tạo Admin user...")

admin_user, created = User.objects.get_or_create(
    username="admin",
    defaults=dict(
        role=RoleEnum.ADMIN,
        gender=GenderEnum.MALE,
        fullname="Administrator",
        phone_number="0900000000",
        is_staff=True,
        is_superuser=True
    )
)

if created:
    admin_user.set_password("admin123")
    admin_user.save()
    print(f"   ✅ Tạo admin user: admin")
else:
    print(f"   ⏭️  Admin user đã tồn tại")

# ==============================
# 3. UPDATE PATIENT PROFILES WITH DETAILS
# ==============================
print("\n3️⃣  Cập nhật PatientProfile với thông tin chi tiết...")

patient_details = {
    "patient1": {
        "address": "123 Nguễn Huệ, Q.1, TP.HCM",
        "dob": date(1990, 5, 15)
    },
    "patient2": {
        "address": "456 Tạ Quang Bửu, Q.8, TP.HCM",
        "dob": date(1995, 8, 22)
    }
}

for username, details in patient_details.items():
    try:
        user = User.objects.get(username=username)
        profile = user.patient_profile
        profile.address = details["address"]
        profile.dob = details["dob"]
        profile.save()
        print(f"   ✅ Cập nhật {username}: {details['address']}, DOB: {details['dob']}")
    except Exception as e:
        print(f"   ❌ Lỗi cập nhật {username}: {e}")

# ==============================
# 4. CREATE MULTIPLE SCHEDULES FOR FUTURE DAYS
# ==============================
print("\n4️⃣  Tạo schedules cho nhiều ngày trong tuần...")

doctor_users = User.objects.filter(role=RoleEnum.DOCTOR)[:5]
today = date.today()

# Tạo schedules cho 7 ngày tiếp theo
new_schedules_count = 0
for offset in range(1, 8):
    work_date = today + timedelta(days=offset)
    
    # Bỏ qua thứ 7 và chủ nhật
    if work_date.weekday() >= 5:
        continue
    
    for doctor_user in doctor_users:
        schedule, created = DoctorSchedule.objects.get_or_create(
            doctor=doctor_user.doctor_profile,
            work_date=work_date,
            defaults=dict(
                start_time=time(8, 0),
                end_time=time(17, 0)
            )
        )
        
        if created:
            new_schedules_count += 1
            print(f"   ✅ {doctor_user.username}: {work_date}")

print(f"   📊 Tổng schedules mới tạo: {new_schedules_count}")

# ==============================
# 5. CREATE APPOINTMENTS FOR FUTURE DATES
# ==============================
print("\n5️⃣  Tạo appointments cho các ngày trong tuần...")

patient_profiles = PatientProfile.objects.all()[:2]
available_slots = TimeSlot.objects.filter(status=SlotStatus.AVAILABLE)[:20]

new_appointments_count = 0
for i, slot in enumerate(available_slots):
    # Đảm bảo mỗi appointment không được tạo lại
    existing = Appointment.objects.filter(
        patient=patient_profiles[i % len(patient_profiles)],
        time_slot=slot
    ).exists()
    
    if not existing:
        appointment = Appointment.objects.create(
            patient=patient_profiles[i % len(patient_profiles)],
            doctor=slot.schedule.doctor,
            time_slot=slot,
            status=AppointmentStatus.BOOKED,
            symptoms=f"Khám sức khỏe định kỳ - Appointment #{i+1}"
        )
        
        # Update slot status
        slot.status = SlotStatus.BOOKED
        slot.save()
        
        new_appointments_count += 1
        if new_appointments_count <= 5:
            print(f"   ✅ Appointment: {appointment.patient.user.username} - "
                  f"{slot.schedule.work_date} {slot.start_time}")

print(f"   📊 Tổng appointments mới tạo: {new_appointments_count}")

# ==============================
# 6. CREATE NOTIFICATIONS FOR ALL APPOINTMENTS
# ==============================
print("\n6️⃣  Tạo Notifications cho appointments...")

all_appointments = Appointment.objects.all()
new_notifications_count = 0

for appointment in all_appointments:
    # Tạo notification cho bệnh nhân
    patient_notification, created = Notification.objects.get_or_create(
        user=appointment.patient.user,
        appointment=appointment,
        defaults=dict(
            message=f"Lịch khám được xác nhận với Bác sĩ {appointment.doctor.user.fullname} "
                   f"vào {appointment.time_slot.schedule.work_date} lúc {appointment.time_slot.start_time}",
            status=NotificationStatus.PENDING
        )
    )
    if created:
        new_notifications_count += 1
    
    # Tạo notification cho bác sĩ
    doctor_notification, created = Notification.objects.get_or_create(
        user=appointment.doctor.user,
        appointment=appointment,
        defaults=dict(
            message=f"Bệnh nhân {appointment.patient.user.fullname} sẽ khám vào "
                   f"{appointment.time_slot.schedule.work_date} lúc {appointment.time_slot.start_time}",
            status=NotificationStatus.PENDING
        )
    )
    if created:
        new_notifications_count += 1

print(f"   ✅ Tổng notifications mới tạo: {new_notifications_count}")

# ==============================
# 7. STATISTICS
# ==============================
print("\n" + "=" * 50)
print("📊 THỐNG KÊ HOÀN THIỆN DỮ LIỆU")
print("=" * 50)

stats = {
    "👥 Tổng Users": User.objects.count(),
    "👨‍⚕️ Bác sĩ": User.objects.filter(role=RoleEnum.DOCTOR).count(),
    "🏥 Bệnh nhân": User.objects.filter(role=RoleEnum.PATIENT).count(),
    "👩‍💼 Lễ tân": User.objects.filter(role=RoleEnum.RECEPTIONIST).count(),
    "👤 Admin": User.objects.filter(role=RoleEnum.ADMIN).count(),
    "📅 Schedules": DoctorSchedule.objects.count(),
    "⏰ Time Slots": TimeSlot.objects.count(),
    "📋 Appointments": Appointment.objects.count(),
    "🔔 Notifications": Notification.objects.count(),
}

for key, value in stats.items():
    print(f"{key}: {value}")

print("\n✨ HOÀN TẤT! DỮ LIỆU ĐÃ ĐƯỢC HOÀN THIỆN")
print("=" * 50)
