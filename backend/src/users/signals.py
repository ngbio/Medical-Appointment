from django.db.models.signals import post_save
from django.dispatch import receiver
from users.models import User, PatientProfile, RoleEnum


@receiver(post_save, sender=User)
def create_patient_profile(sender, instance, created, **kwargs):
    if created and instance.role == RoleEnum.PATIENT:
        PatientProfile.objects.create(user=instance)