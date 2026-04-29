from django.db.models.signals import post_save
from django.dispatch import receiver
from appointments.models import Appointment
from appointments.tasks import send_appointment_confirmation

@receiver(post_save, sender=Appointment)
def appointment_created(sender, instance, created, **kwargs):
    if created:
        send_appointment_confirmation.delay(instance.id)