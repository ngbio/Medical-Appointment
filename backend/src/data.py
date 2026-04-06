from datetime import date, time, datetime, timedelta
from django.contrib.auth import get_user_model
from users.models import RoleEnum, GenderEnum
from doctors.models import Specialty, DoctorProfile, DoctorSchedule, TimeSlot, SlotStatus
from appointments.models import Appointment, AppointmentStatus 

User = get_user_model()

print("=== BẮT ĐẦU NẠP DỮ LIỆU ===")

# 1. Xóa dữ liệu cũ
print("1. Đang dọn dẹp dữ liệu cũ...")
User.objects.filter(username__in=['patient1', 'patient2', 'doctor1', 'doctor2', 'doctor3']).delete()
Specialty.objects.all().delete()

# 2. Tạo Chuyên khoa
print("2. Đang tạo Chuyên khoa...")
spec1, _ = Specialty.objects.get_or_create(name='Khoa Tim mạch')
spec2, _ = Specialty.objects.get_or_create(name='Khoa Da liễu')
spec3, _ = Specialty.objects.get_or_create(name='Khoa Thần kinh')

# 3. Tạo User & Profile
print("3. Đang tạo Users (Bệnh nhân & Bác sĩ)...")
p1_user = User.objects.create_user(username='patient1', password='123', role=RoleEnum.PATIENT, gender=GenderEnum.MALE, fullname='Bệnh nhân A', phone_number='0111')
p2_user = User.objects.create_user(username='patient2', password='123', role=RoleEnum.PATIENT, gender=GenderEnum.FEMALE, fullname='Bệnh nhân B', phone_number='0222')

d1_user = User.objects.create_user(username='doctor1', password='123', role=RoleEnum.DOCTOR, gender=GenderEnum.MALE, fullname='Bác sĩ Nguyễn Văn A', phone_number='0991')
d1_profile = DoctorProfile.objects.create(user=d1_user, specialty=spec1, experience_years=5)

d2_user = User.objects.create_user(username='doctor2', password='123', role=RoleEnum.DOCTOR, gender=GenderEnum.FEMALE, fullname='Bác sĩ Trần Thị B', phone_number='0992')
d2_profile = DoctorProfile.objects.create(user=d2_user, specialty=spec2, experience_years=8)

d3_user = User.objects.create_user(username='doctor3', password='123', role=RoleEnum.DOCTOR, gender=GenderEnum.MALE, fullname='Bác sĩ Lê Văn C', phone_number='0993')
d3_profile = DoctorProfile.objects.create(user=d3_user, specialty=spec3, experience_years=12)

# 4. Tạo Lịch & Time Slots
print("4. Đang tạo Lịch làm việc và TimeSlots...")
today = date.today()
all_slots = []
doctors = [d1_profile, d2_profile, d3_profile]

for doc in doctors:
    schedule = DoctorSchedule.objects.create(doctor=doc, work_date=today, start_time=time(8, 0), end_time=time(12, 0))
    start_dt = datetime.combine(today, time(8, 0))
    
    for i in range(8): # 8 slots
        slot_start = (start_dt + timedelta(minutes=30*i)).time()
        slot_end = (start_dt + timedelta(minutes=30*(i+1))).time()
        slot = TimeSlot(schedule=schedule, start_time=slot_start, end_time=slot_end, status=SlotStatus.AVAILABLE)
        all_slots.append(slot)

TimeSlot.objects.bulk_create(all_slots)

# 5. Tạo Cuộc hẹn
print("5. Đang tạo Cuộc hẹn (Appointments)...")
patients = [p1_user.patient_profile, p2_user.patient_profile]
slots_from_db = list(TimeSlot.objects.all()[:10])

for i in range(10):
    slot = slots_from_db[i]
    slot.status = SlotStatus.BOOKED
    slot.save()
    
    Appointment.objects.create(
        patient=patients[i % 2],
        doctor=slot.schedule.doctor,
        time_slot=slot,
        status=AppointmentStatus.BOOKED,
        symptoms=f'Bệnh nhân đau đầu cấp độ {i+1}'
    )

print("🎉 HOÀN TẤT TẠO DỮ LIỆU! BẠN CÓ THỂ MỞ POSTMAN LÊN TEST.")