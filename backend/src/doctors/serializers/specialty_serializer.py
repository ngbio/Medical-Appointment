from rest_framework.serializers import ModelSerializer
from rest_framework.exceptions import ValidationError
from ..models import Specialty

class SpecialtySerializer(ModelSerializer):
    class Meta:
        model = Specialty
        fields = ['id', 'name']
        read_only_fields = ['id']

    def validate_name(self, value):
        if Specialty.objects.filter(name=value).exists():
            raise ValidationError("A specialty with this name already exists.")
        return value