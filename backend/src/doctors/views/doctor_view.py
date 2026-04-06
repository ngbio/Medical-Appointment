from rest_framework import viewsets, parsers, permissions, mixins, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from ..models import DoctorProfile
from ..serializers.doctor_serializer import DoctorProfileSerializer
from ..paginators import DoctorProfileCursorPagination
from src.perms import IsOwner
from users.models import RoleEnum
from doctors.perms import IsDoctor

class DoctorProfileViewSet(viewsets.GenericViewSet,
                           mixins.ListModelMixin,
                           mixins.CreateModelMixin,
                           mixins.UpdateModelMixin,
                           mixins.DestroyModelMixin,):
    serializer_class = DoctorProfileSerializer
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]
    pagination_class = DoctorProfileCursorPagination
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        user = self.request.user

        queryset = DoctorProfile.objects.select_related('user', 'specialty').all()

        if getattr(user, "role", None) == RoleEnum.DOCTOR:
            queryset = queryset.filter(user=user)

      
        if self.action == 'list':
            query_params = self.request.query_params
            
            specialty_id = query_params.get('speciality_id')
            filter_date = query_params.get('date')

            if specialty_id:
                queryset = queryset.filter(specialty_id=specialty_id)

            if filter_date:
                queryset = queryset.filter(schedules__work_date=filter_date).distinct()

        return queryset

    def get_permissions(self):
        if self.action in ['create', 'destroy']:
            permission_classes = [permissions.IsAdminUser]
        elif self.action in ['partial_update']:
            permission_classes = [IsOwner | permissions.IsAdminUser]
        else:
            permission_classes = [permissions.AllowAny]

        return [permission() for permission in permission_classes]

    
    # Deactivate the user instead of deleting the doctor profile
    def perform_destroy(self, instance):
        doctor_user = instance.user
        doctor_user.is_active = False  
        doctor_user.save()

        instance.delete()

    @action(methods=['get', 'patch'], detail=False, url_path='me', permission_classes=[permissions.IsAuthenticated, IsDoctor])
    def me(self, request):
        user = request.user

        try:
            doctor_profile = DoctorProfile.objects.get(user=user)
        except DoctorProfile.DoesNotExist:
            raise ValidationError("Doctor profile does not exist.")
        
        if request.method == 'GET':
            serializer = self.get_serializer(doctor_profile)
            return Response(serializer.data)

        if request.method == 'PATCH':
            serializer = self.get_serializer(
                doctor_profile,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(serializer.data, status=status.HTTP_200_OK)
    
