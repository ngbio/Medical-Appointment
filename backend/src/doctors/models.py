from django.db import models
from users.models import User

class Specialty(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    
class DoctorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    specialty = models.ForeignKey(Specialty, on_delete=models.SET_NULL, null=True, blank=True)
    bio = models.TextField(blank=True)
    experience_years = models.IntegerField(default=0)

    def __str__(self):
        return f"Doctor Profile for {self.user.username}"

class DoctorSchedule(models.Model):
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='schedules', unique=True)
    work_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()


    def __str__(self):
        return f"Schedule for {self.doctor.user.username} on {self.date} from {self.start_time} to {self.end_time}"

class SlotStatus(models.TextChoices):
    AVAILABLE = 'available', 'Available'
    BOOKED = 'booked', 'Booked'
    BLOCKED = 'blocked', 'Blocked'

class TimeSlot(models.Model):
    schedule = models.ForeignKey(DoctorSchedule, on_delete=models.CASCADE, related_name='time_slots')
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=10, choices=SlotStatus.choices, default=SlotStatus.AVAILABLE)

    class Meta:
        unique_together = ('schedule', 'start_time', 'end_time')

    def __str__(self):
        return f"Time Slot for {self.schedule.doctor.user.username} on {self.schedule.work_date} from {self.start_time} to {self.end_time}"