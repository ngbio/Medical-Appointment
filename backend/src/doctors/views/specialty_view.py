from rest_framework import viewsets, parsers, permissions, mixins

from ..models import Specialty
from ..serializers.specialty_serializer import SpecialtySerializer

class SpecialtyViewSet(viewsets.GenericViewSet,
                        mixins.ListModelMixin,
                        mixins.CreateModelMixin,
                        mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin):
    
    queryset = Specialty.objects.all()
    serializer_class = SpecialtySerializer
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]
    http_method_names = ['get', 'post', 'patch', 'delete']
    
    def get_permissions(self):
        if self.action in ['create', 'destroy', 'partial_update']:
            permission_classes = [permissions.IsAdminUser]
        else:
            permission_classes = [permissions.AllowAny]

        return [permission() for permission in permission_classes]
    