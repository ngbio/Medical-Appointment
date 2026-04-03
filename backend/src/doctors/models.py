from django.db import models
from users.models import User
from datetime import date, time
from django.core.exceptions import ValidationError

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
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='schedules')
    work_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()


    def __str__(self):
        return f"Schedule for {self.doctor.user.username} on {self.work_date} from {self.start_time} to {self.end_time}"
    
    def clean(self):
        errors = {}

        if self.work_date < date.today():
            errors['work_date'] = "Work date cannot be in the past."

        if self.start_time < time(8, 0):
            errors['start_time'] = "Start time must be after 08:00."

        if self.end_time > time(20, 0):
            errors['end_time'] = "End time must be before 20:00."

        # Start < End
        if self.start_time >= self.end_time:
            errors['end_time'] = "End time must be after start time."

        # Overlap schedule
        overlapping = DoctorSchedule.objects.filter(
            doctor=self.doctor,
            work_date=self.work_date,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time
        )

        if self.pk:
            overlapping = overlapping.exclude(pk=self.pk)

        if overlapping.exists():
            errors['__all__'] = "This schedule overlaps with another schedule."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

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