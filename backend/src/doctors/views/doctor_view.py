from rest_framework import viewsets, parsers, permissions, mixins, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from django.shortcuts import render
from django.utils.timezone import now

from ..models import DoctorProfile
from ..serializers.doctor_serializer import DoctorProfileSerializer
from ..paginators import DoctorProfileCursorPagination
from src.perms import IsOwner
from users.models import RoleEnum
from doctors.perms import IsDoctor
from appointments.models import Appointment

class DoctorProfileViewSet(viewsets.GenericViewSet,
                           mixins.ListModelMixin,
                           mixins.UpdateModelMixin):
    serializer_class = DoctorProfileSerializer
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]
    pagination_class = DoctorProfileCursorPagination
    http_method_names = ['get', 'patch']

    def get_queryset(self):
        user = self.request.user

        queryset = DoctorProfile.objects.select_related(
            'user', 'specialty').prefetch_related(
            'schedules'
        )

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
        if self.action in ['partial_update']:
            return [(IsOwner | permissions.IsAdminUser)()]
        elif self.action in ['me', 'dashboard']:
            return [permissions.IsAuthenticated(), IsDoctor()]

        return [permissions.AllowAny()]


    @action(methods=['get', 'patch'], detail=False, url_path='me', permission_classes=[permissions.IsAuthenticated(), IsDoctor()])
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
        
    @action(methods=['get'], detail=False, url_path='dashboard', permission_classes=[permissions.IsAuthenticated(), IsDoctor()])
    def dashboard(self, request):
        user = request.user

        try:
            doctor_profile = DoctorProfile.objects.get(user_id=user.id)
        except DoctorProfile.DoesNotExist:
            raise ValidationError("Doctor profile does not exist.")
        
        today = now().date()

        # Today's appointments
        today_count = Appointment.objects.filter(
            doctor=doctor_profile,
            time_slot__schedule__work_date=today
        ).count()

        # Upcoming appointments
        upcoming = Appointment.objects.filter(
            doctor=doctor_profile,
            time_slot__schedule__work_date__gte=today
        ).select_related(
            "patient__user",
            "time_slot__schedule"
        ).order_by("time_slot__schedule__work_date", "time_slot__start_time")

        return Response({
            "today_count": today_count,
            "upcoming_count": upcoming.count(),
            "appointments": [
                {   
                    "id": a.id,
                    "patient": a.patient.user.fullname,
                    # "date": str(a.time_slot.schedule.work_date),
                    "time": str(a.time_slot.start_time),
                    "status": a.status
                }
                for a in upcoming[:5]
            ]
        })



def doctor_dashboard(request):
    return render(request, "doctor/dashboard_doctor.html")