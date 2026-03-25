from rest_framework import serializers
from users.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "password", "fullname", "email", "phhone_number", "gender", "role")

        extra_kwargs = {
            "password": {"write_only": True, }
        }

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        u = User(**validated_data)
        if password:
            u.set_password(password)
        u.save()

        return u

    def to_representation(self, instance):
        data = super().to_representation(instance)

        return data
