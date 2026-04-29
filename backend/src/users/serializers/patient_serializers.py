from rest_framework import serializers
from users.models import PatientProfile
from users.serializers.user_serializers import UserSerializer
from datetime import date

class PatientProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=False)

    class Meta:
        model = PatientProfile
        fields = ['id', 'user', 'address', 'dob']
        read_only_fields = ['id']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.partial:
            self.fields["user"].partial = True

    def validate_dob(self, value):
        if value and value > date.today():
            raise serializers.ValidationError("Date of birth cannot be in the future.")
        return value

    def validate(self, attrs):
        address = attrs.get('address')

        if address is not None and address.strip() == "":
            raise serializers.ValidationError({
                "address": "Address cannot be empty."
            })

        return attrs

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if user_data:
            user_serializer = self.fields['user']
            
            if 'user' in getattr(self, 'initial_data', {}):
                user_serializer.initial_data = self.initial_data['user']
            
            user_serializer.partial = True
            user_serializer.update(instance.user, user_data)

        return instance