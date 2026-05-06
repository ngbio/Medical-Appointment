from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from appointments.models import Appointment
from appointments.tasks import send_appointment_confirmation


@receiver(post_save, sender=Appointment)
def send_appointment_confirmation_email(sender, instance, created, **kwargs):
    if not created:
        return


    # Send confirmation email asynchronously
    send_appointment_confirmation.delay(instance.id)
