from rest_framework import serializers
from users.models import RoleEnum, PatientProfile, User
from django.db import transaction
from rest_framework.exceptions import ValidationError
import re


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "password", "fullname", "email", "phone_number", "gender", "role")

        extra_kwargs = {
            "password": {"write_only": True, },
            "role": {"read_only": True, },
        }

    def validate_email_syntax(self, value):
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(pattern, value):
            raise ValidationError("Invalid email")
        return value
    
    def validate_phone_number(self, value):
        if not re.match(r'^\d{10,11}$', value):
            raise serializers.ValidationError("Invalid phone number")
        return value


    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.avatar:
            data["avatar"] = instance.avatar.url
        return data

    def create(self, validated_data):
        password = validated_data.pop("password", None)

        # If create new user, auto create patient profile for them
        with transaction.atomic():
            u = User(**validated_data)
            if password:
                u.set_password(password)
            u.save()

        return u

    def update(self, instance, validated_data):

        # update password
        new_password = validated_data.pop("password", None)

        if new_password:
            old_password = self.initial_data.get("old_password")

            if not old_password:
                raise ValidationError({"old_password": "YOU NEED PROVIDE YOUR OLD PASSWORD!"})
            if not instance.check_password(old_password):
                raise ValidationError({"old_password": "YOUR OLD PASSWORD IS INCORRECT!"})

            instance.set_password(new_password)
            instance.save()

        # update other fields
        allowed_fields = {"fullname", "email", "phone_number"}

        if set(validated_data.keys()) - allowed_fields:
            raise ValidationError({"error": "THIS FIELD CANNOT BE UPDATED"})

        return super().update(instance, validated_data)
