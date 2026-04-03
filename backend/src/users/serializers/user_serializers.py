from rest_framework import serializers
from users.models import RoleEnum, PatientProfile, User
from django.db import transaction
from rest_framework.exceptions import ValidationError


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "password", "fullname", "email", "phone_number", "gender", "role")

        extra_kwargs = {
            "password": {"write_only": True, },
            "role": {"read_only": True, },
        }

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.avatar:
            data["avatar"] = instance.avatar.url
        return data

    def create(self, validated_data):
        avatar = validated_data.pop("avatar", None)
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
