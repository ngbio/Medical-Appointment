from rest_framework.serializers import ModelSerializer
from rest_framework.exceptions import ValidationError
from ..models import DoctorProfile
from users.models import RoleEnum

class DoctorProfileSerializer(ModelSerializer):
    class Meta:
        model = DoctorProfile
        fields = ['id', 'user', 'specialty', 'bio', 'experience_years']
        read_only_fields = ['id']

    def validate_experience_years(self, value):
        if value < 0:
            raise ValidationError("Experience years cannot be negative.")
        return value
    
    def create(self, validated_data):
        user = validated_data.get('user')
        
        # Check if the user has doctor role
        if user.role != RoleEnum.DOCTOR:
            raise ValidationError("The user must have a doctor role to create a doctor profile.")
        
        # Check if the user already has a doctor profile
        if DoctorProfile.objects.filter(user=user).exists():
            raise ValidationError("This user already has a doctor profile.")
        
        doctor_profile = DoctorProfile.objects.create(user=user, **validated_data)
        return doctor_profile
    
    def update(self, instance, validated_data):
        user = self.context['request'].user
        
        # Ensure that the user can only update their own doctor profile
        if instance.user != user and user.role == RoleEnum.DOCTOR:
            raise ValidationError("You can only update your own doctor profile.")
        
        return super().update(instance, validated_data)
