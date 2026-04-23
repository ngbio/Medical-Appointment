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


    def validate_username(self, value):
        """Validate username"""
        if not value:
            raise ValidationError("Tên đăng nhập không được để trống!")
        if len(value) < 3:
            raise ValidationError("Tên đăng nhập phải ít nhất 3 ký tự!")
        if len(value) > 50:
            raise ValidationError("Tên đăng nhập không được vượt quá 50 ký tự!")
        if not re.match("^[a-zA-Z0-9_]*$", value):
            raise ValidationError("Tên đăng nhập chỉ chứa chữ, số và dấu gạch dưới!")
        return value

    def validate_password(self, value):
        """Validate password"""
        if not value:
            raise ValidationError("Mật khẩu không được để trống!")
        if len(value) < 6:
            raise ValidationError("Mật khẩu phải ít nhất 6 ký tự!")
        return value

    def validate_email(self, value):
        """Validate email"""
        if value and not re.match(r'^[^@]+@[^@]+\.[^@]+$', value):
            raise ValidationError("Email không hợp lệ!")
        return value

    def validate_phone_number(self, value):
        """Validate phone number"""
        if not value:
            raise ValidationError("Số điện thoại không được để trống!")
        if not re.match(r'^[0-9]{10,11}$', value):
            raise ValidationError("Số điện thoại phải là 10-11 chữ số!")
        return value

    def validate_fullname(self, value):
        """Validate fullname"""
        if value and len(value) > 255:
            raise ValidationError("Họ tên không được vượt quá 255 ký tự!")
        return value

    def validate(self, data):
        """Validate entire data"""
        if 'gender' in data and data['gender'] not in dict(data.get('gender', 'choices', [])):
            if data['gender'] not in ['male', 'female']:
                raise ValidationError({"gender": "Giới tính không hợp lệ! Chọn 'male' hoặc 'female'"})
        return data
>>>>>>> feature/docker-setup

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
