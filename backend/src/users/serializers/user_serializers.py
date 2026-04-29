from rest_framework import serializers
from users.models import User
from django.db import transaction
from rest_framework.exceptions import ValidationError
import re
from users.tasks import send_email_confirmation


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
        if value is None:
            return value
        if value == "":
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
        if value in [None, ""]:
            if self.partial:
                return value
            raise ValidationError("Số điện thoại không được để trống!")

        if not re.match(r'^[0-9]{10,11}$', value):
            raise ValidationError("Số điện thoại phải là 10-11 chữ số!")

        return value

    def validate_fullname(self, value):
        """Validate fullname"""
        if value and len(value) > 255:
            raise ValidationError("Họ tên không được vượt quá 255 ký tự!")
        return value
    
    def validate_gender(self, value):
        """Validate gender"""
        if value not in ['male', 'female']:
            raise ValidationError("Giới tính không hợp lệ!")
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

        request = self.context.get("request")
        if request is not None:
            confirmation_url = request.build_absolute_uri(f"/confirm-email/{u.fullname}/")
        else:
            confirmation_url = ""

        # Send confirmation email asynchronously
        send_email_confirmation.delay(u.id, confirmation_url)

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
        allowed_fields = {"fullname", "email", "phone_number", "gender"}

        if set(validated_data.keys()) - allowed_fields:
            raise ValidationError({"error": "THIS FIELD CANNOT BE UPDATED"})
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
