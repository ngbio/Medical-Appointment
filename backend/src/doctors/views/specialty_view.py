from doctors.paginators import SpecialtyCursorPagination
from rest_framework import viewsets, parsers, permissions, mixins

from ..models import Specialty
from ..serializers.specialty_serializer import SpecialtySerializer

class SpecialtyViewSet(viewsets.GenericViewSet,
                        mixins.ListModelMixin):
    
    queryset = Specialty.objects.all()
    serializer_class = SpecialtySerializer
    http_method_names = ['get']
    permission_classes = [permissions.AllowAny]
    pagination_class = SpecialtyCursorPagination