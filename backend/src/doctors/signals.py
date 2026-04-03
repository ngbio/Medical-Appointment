from django.db.models.signals import post_save
from django.dispatch import receiver
from doctors.models import DoctorSchedule
from doctors.services.timeslot_service import generate_timeslots

@receiver(post_save, sender=DoctorSchedule)
def create_timeslots_for_schedule(sender, instance, created, **kwargs):
    # Auto generate timeslots when a new schedule is created
    
    if not created: # only generate timeslots when a new schedule is created, not when it's updated
        return

    # Generate timeslots for the new schedule
    generate_timeslots(schedule=instance)