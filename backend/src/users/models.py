from django.db import models
from django.contrib.auth.models import AbstractUser
from rest_framework.exceptions import ValidationError

class RoleEnum(models.TextChoices):
    ADMIN = 'admin', 'Admin'
    PATIENT = 'patient', 'Patient'
    DOCTOR = 'doctor', 'Doctor'
    RECEPTIONIST = 'receptionist', 'Receptionist'

class GenderEnum(models.TextChoices):
    MALE = 'male', 'Male'
    FEMALE = 'female', 'Female'

AbstractUser.username.field.error_messages['unique'] = 'Tên đăng nhập đã tồn tại!'
class User(AbstractUser):
    fullname = models.CharField(max_length=255)
    phhone_number = models.CharField(max_length=10)
    gender = models.CharField(max_length=10, choices=GenderEnum.choices)
    role = models.CharField(max_length=20, choices=RoleEnum.choices, default=RoleEnum.PATIENT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class PatientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    address = models.CharField(max_length=255, blank=True)
    dob = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Patient Profile for {self.user.username}"
