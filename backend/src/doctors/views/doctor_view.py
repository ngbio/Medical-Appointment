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
from appointments.models import Appointment, AppointmentStatus
from appointments.serializers.appointment_serializers import AppointmentSerializer
from appointments.paginators import AppointmentsPagination
from appointments.services.query_service import get_base_queryset

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
        # today_qs = Appointment.objects.filter(doctor=doctor_profile, time_slot__schedule__work_date=today).select_related("patient__user", "time_slot__schedule")
        today_count = get_base_queryset().filter(doctor=doctor_profile, work_date=today).count()

        # Scheduled appointments
        # scheduled_count = today_qs.filter(status=AppointmentStatus.BOOKED).count()
        scheduled_qs = get_base_queryset().filter(doctor=doctor_profile, work_date=today, status=AppointmentStatus.BOOKED)
        scheduled_count = scheduled_qs.count()

        paginator = AppointmentsPagination()
        page = paginator.paginate_queryset(scheduled_qs, request)
        serializer = AppointmentSerializer(page, many=True)
        response = paginator.get_paginated_response(serializer.data)

        response.data.update({
            "today_count": today_count,
            "scheduled_count": scheduled_count,
        })

        return response
    
    def examination_list(self, request):
        user = request.user

        try:
            doctor_profile = DoctorProfile.objects.get(user_id=user.id)
        except DoctorProfile.DoesNotExist:
            raise ValidationError("Doctor profile does not exist.")
        
        appointments_qs = get_base_queryset().filter(doctor=doctor_profile).order_by("-work_date", "-start_time")
        paginator = AppointmentsPagination()
        page = paginator.paginate_queryset(appointments_qs, request)
        serializer = AppointmentSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


def doctor_dashboard(request):
    return render(request, "doctor/dashboard_doctor.html")

def doctor_schedule(request):
    return render(request, "doctor/doctor_schedule.html")

def doctor_examination_list(request):
    return render(request, "doctor/appointment_list.html")

def doctor_examination_detail(request, appointment_id):
    return render(request, "doctor/appointment_detail.html", {"appointment_id": appointment_id} )