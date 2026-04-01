from rest_framework import viewsets, parsers, permissions, mixins, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from datetime import datetime
from ..serializers.schedule_serializer import ScheduleSerializer
from doctors.models import DoctorSchedule
from users.models import RoleEnum
from ..services.schedule_service import get_doctor_schedules, get_schedules_by_doctor, get_available_slots
from doctors.serializers.timeslot_serializer import TimeSlotSerializer

class ScheduleViewSet(viewsets.GenericViewSet,
                      mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin):
    
    serializer_class = ScheduleSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        user = self.request.user

        if not user.is_authenticated:
            return DoctorSchedule.objects.none()

        # Doctor only can see their own schedule
        if user.role == RoleEnum.DOCTOR:
            return DoctorSchedule.objects.filter(doctor__user=user)

        return DoctorSchedule.objects.all()
    
    def get_permissions(self):
        if self.action in ['create', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAdminUser]
        elif self.action in ['available_slots', 'by_doctor']:
            return [permissions.AllowAny()]
        else:
            permission_classes = [permissions.IsAuthenticated]

        return [permission() for permission in permission_classes]

    @action(methods=['get'], detail=False, url_path='my-schedules', permission_classes=[permissions.IsAuthenticated])
    def my_schedules(self, request):
        schedules = get_doctor_schedules(
            user=request.user,
            date_str=request.query_params.get('date')
        )

        serializer = self.get_serializer(schedules, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=False, url_path='by-doctor')
    def by_doctor(self, request):
        schedules = get_schedules_by_doctor(
            doctor_id=request.query_params.get('doctor_id'),
            date_str=request.query_params.get('date')
        )

        serializer = self.get_serializer(schedules, many=True)
        return Response(serializer.data)
    
    @action(methods=['get'], detail=False, url_path='available-slots')
    def available_slots(self, request):
        slots = get_available_slots(
            schedule_id=request.query_params.get('schedule_id')
        )

        
        serializer = TimeSlotSerializer(slots, many=True)
        return Response(serializer.data)