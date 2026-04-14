from doctors.perms import IsDoctor
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from datetime import datetime
from ..serializers.schedule_serializer import ScheduleSerializer
from doctors.models import DoctorSchedule
from users.models import RoleEnum
from ..services.schedule_service import get_doctor_schedules, get_schedules_by_doctor, get_available_slots
from doctors.serializers.timeslot_serializer import TimeSlotSerializer

class ScheduleViewSet(viewsets.GenericViewSet):
    
    serializer_class = ScheduleSerializer
    http_method_names = ['get']
    queryset = DoctorSchedule.objects.all()
    
    
    def get_permissions(self):
        if self.action == 'my_schedules':
            return [permissions.IsAuthenticated(), IsDoctor()]

        # public APIs
        if self.action in ['by_doctor', 'available_slots']:
            return [permissions.AllowAny()]

        return [permissions.AllowAny()]

    @action(methods=['get'], detail=False, url_path='my-schedules')
    def my_schedules(self, request):
        schedules = get_doctor_schedules(
            user=request.user,
            date_str=request.query_params.get('date')
        )

        serializer = self.get_serializer(schedules, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=False, url_path='by-doctor')
    def by_doctor(self, request):
        doctor_id = request.query_params.get('doctor_id')
        date_str = request.query_params.get('date')

        if not doctor_id:
            return Response({"detail": "doctor_id is required."}, status=400)

        schedules = get_schedules_by_doctor(
            doctor_id=doctor_id,
            date_str=date_str 
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