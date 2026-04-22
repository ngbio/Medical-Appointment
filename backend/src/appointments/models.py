from django.db import models
from users.models import PatientProfile
from doctors.models import DoctorProfile, TimeSlot

class AppointmentStatus(models.TextChoices):
    BOOKED = 'scheduled', 'Scheduled'
    COMPLETED = 'completed', 'Completed'
    CANCELED = 'canceled', 'Canceled'

class Appointment(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='appointments')
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE, related_name='appointments')
    status = models.CharField(max_length=10, choices=AppointmentStatus.choices, default=AppointmentStatus.BOOKED)
    symptoms = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Appointment for {self.patient.user.username} with Dr. {self.doctor.user.username} on {self.time_slot.schedule.work_date} at {self.time_slot.start_time}"


