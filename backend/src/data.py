import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings')
django.setup()

from datetime import date, time, datetime, timedelta
from django.contrib.auth import get_user_model
from users.models import RoleEnum, GenderEnum
from doctors.models import Specialty, DoctorProfile, DoctorSchedule, TimeSlot, SlotStatus
from appointments.models import Appointment, AppointmentStatus

User = get_user_model()

if User.objects.filter(username__startswith=("patient", "doctor")).exists():
    print("=== DATA ĐÃ TỒN TẠI, BỎ QUA SEED ===")
else:

    print("=== BẮT ĐẦU NẠP DỮ LIỆU ===")

    # ==============================
    # 1. CLEAN DATA
    # ==============================
    print("1. Cleaning old data...")

    Appointment.objects.all().delete()
    TimeSlot.objects.all().delete()
    DoctorSchedule.objects.all().delete()
    DoctorProfile.objects.all().delete()

    User.objects.filter(
        username__startswith=("patient", "doctor")
    ).delete()

    Specialty.objects.all().delete()

    # ==============================
    # 2. SPECIALTIES
    # ==============================
    print("2. Creating specialties...")

    specs = {
        "cardio": Specialty.objects.create(name="Khoa Tim mạch"),
        "derma": Specialty.objects.create(name="Khoa Da liễu"),
        "neuro": Specialty.objects.create(name="Khoa Thần kinh"),
    }

    # ==============================
    # 3. USERS
    # ==============================
    print("3. Creating users...")

    def create_user(username, password, role, gender, fullname, phone):
        user, created = User.objects.get_or_create(
            username=username,
            defaults=dict(
                role=role,
                gender=gender,
                fullname=fullname,
                phone_number=phone
            )
        )

        if created:
            user.set_password(password)
            user.save()
            print(f"✅ Created user: {username}")

        return user

    users_data = [
        ("patient1", "123", RoleEnum.PATIENT, GenderEnum.MALE, "Bệnh nhân A", "0111"),
        ("patient2", "123", RoleEnum.PATIENT, GenderEnum.FEMALE, "Bệnh nhân B", "0222"),

        ("doctor1", "123", RoleEnum.DOCTOR, GenderEnum.MALE, "BS A", "0991"),
        ("doctor2", "123", RoleEnum.DOCTOR, GenderEnum.FEMALE, "BS B", "0992"),
        ("doctor3", "123", RoleEnum.DOCTOR, GenderEnum.MALE, "BS C", "0993"),
        ("doctor4", "123", RoleEnum.DOCTOR, GenderEnum.MALE, "BS D", "0994"),
        ("doctor5", "123", RoleEnum.DOCTOR, GenderEnum.FEMALE, "BS E", "0995"),
        ("doctor6", "123", RoleEnum.DOCTOR, GenderEnum.MALE, "BS F", "0996"),
        ("doctor7", "123", RoleEnum.DOCTOR, GenderEnum.FEMALE, "BS G", "0997"),
        ("doctor8", "123", RoleEnum.DOCTOR, GenderEnum.MALE, "BS H", "0998"),
    ]

    user_map = {}

    for data in users_data:
        user = create_user(*data)
        user_map[user.username] = user

    # ==============================
    # 4. DOCTOR PROFILES
    # ==============================
    print("4. Creating doctor profiles...")

    doctor_profiles_data = [
        ("doctor1", "cardio", 5),
        ("doctor2", "derma", 8),
        ("doctor3", "neuro", 12),
        ("doctor4", "cardio", 10),
        ("doctor5", "derma", 7),
        ("doctor6", "cardio", 6),
        ("doctor7", "derma", 9),
        ("doctor8", "neuro", 11),
    ]

    doctor_profiles = []

    for username, spec_key, exp in doctor_profiles_data:
        user = user_map[username]

        profile, _ = DoctorProfile.objects.get_or_create(user=user)
        profile.specialty = specs[spec_key]
        profile.experience_years = exp
        profile.save()

        doctor_profiles.append(profile)

    # ==============================
    # 5. SCHEDULE + TIMESLOTS
    # ==============================
    print("5. Creating schedules...")

    today = date.today()
    all_slots = []

    for doc in doctor_profiles[:3]:  # chỉ lấy 3 bác sĩ demo
        schedule, _ = DoctorSchedule.objects.get_or_create(
            doctor=doc,
            work_date=today,
            defaults=dict(start_time=time(8, 0), end_time=time(12, 0))
        )

        start_dt = datetime.combine(today, time(8, 0))

        for i in range(8):
            slot_start = (start_dt + timedelta(minutes=30*i)).time()
            slot_end = (start_dt + timedelta(minutes=30*(i+1))).time()

            if not TimeSlot.objects.filter(
                schedule=schedule,
                start_time=slot_start
            ).exists():
                all_slots.append(TimeSlot(
                    schedule=schedule,
                    start_time=slot_start,
                    end_time=slot_end,
                    status=SlotStatus.AVAILABLE
                ))

    TimeSlot.objects.bulk_create(all_slots)

    # ==============================
    # 6. APPOINTMENTS
    # ==============================
    print("6. Creating appointments...")

    patients = [
        user_map["patient1"].patient_profile,
        user_map["patient2"].patient_profile
    ]

    slots = TimeSlot.objects.filter(status=SlotStatus.AVAILABLE)[:10]

    for i, slot in enumerate(slots):
        slot.status = SlotStatus.BOOKED
        slot.save()

        Appointment.objects.get_or_create(
            patient=patients[i % 2],
            doctor=slot.schedule.doctor,
            time_slot=slot,
            defaults=dict(
                status=AppointmentStatus.BOOKED,
                symptoms=f"Đau đầu mức {i+1}"
            )
        )

    print("🎉 HOÀN TẤT! DATA ĐÃ SẴN SÀNG.")