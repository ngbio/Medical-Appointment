from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone
from appointments.models import Appointment, AppointmentStatus
from appointments.serializers.appointment_serializers import AppointmentSerializer
from users.models import RoleEnum
from appointments.paginators import AppointmentsPagination
from doctors.models import SlotStatus
from rest_framework import permissions
from src.perms import IsPatient
from src.perms import IsAdmin
from doctors.perms import IsDoctor
from receptionists.perms import IsReceptionist
from receptionists.serializers.receptionist_serializer import ReceptionistBookSerializer
from appointments.services.query_service import get_base_queryset
from django.shortcuts import render

class AppointmentViewSet(viewsets.GenericViewSet,
                         mixins.ListModelMixin,
                         mixins.CreateModelMixin,
                         mixins.RetrieveModelMixin):
    serializer_class = AppointmentSerializer
    pagination_class = AppointmentsPagination

    def get_permissions(self):
        if self.action == 'create':
            return [IsPatient()]

        elif self.action in ['list', 'retrieve', 'cancel_appointment']:
            return [(IsPatient | permissions.IsAdminUser | IsDoctor)()]
        elif self.action == 'complete_appointment':
            return [IsDoctor()]
        elif self.action in ['book_for_patient', 'dashboard']:
            return [IsReceptionist()]

        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Appointment.objects.none()

        # Queryset cơ bản với select_related để tối ưu
        queryset = get_base_queryset().order_by('-work_date', '-slot_time')

        query_params = self.request.query_params
        status_param = query_params.get('status')
        from_date = query_params.get('from')
        to_date = query_params.get('to')

        if status_param:
            queryset = queryset.filter(status=status_param)
        if from_date and to_date:
            queryset = queryset.filter(
                work_date__range=[from_date, to_date]
            )

        if user.role == RoleEnum.PATIENT:
            return queryset.filter(patient__user=user)

        elif user.role == RoleEnum.DOCTOR:
            return queryset.filter(doctor__user=user)
        
        elif user.role == RoleEnum.ADMIN:
            return queryset

        return Appointment.objects.none()

    def perform_create(self, serializer):
        user = self.request.user

        serializer.save(patient=user.patient_profile)

    @action(methods=['patch'], detail=True, url_path='cancel')
    def cancel_appointment(self, request, pk=None):
        appointment = self.get_object()

        if appointment.status == AppointmentStatus.CANCELED:
            raise ValidationError({"status": "This appointment is already canceled."})

        if appointment.status == AppointmentStatus.COMPLETED:
            raise ValidationError({"status": "Cannot cancel a completed appointment."})


        with transaction.atomic():
            appointment.status = AppointmentStatus.CANCELED
            appointment.save(update_fields=['status'])

            if appointment.time_slot:
                appointment.time_slot.status = SlotStatus.AVAILABLE
                appointment.time_slot.save(update_fields=['status'])

        return Response(
            {"detail": "Appointment canceled successfully.", "status": appointment.status},
            status=status.HTTP_200_OK
        )

    @action(methods=['patch'], detail=True, url_path='complete', permission_classes=[permissions.IsAuthenticated(), IsDoctor()])
    def complete_appointment(self, request, pk=None):
        appointment = self.get_object()
        user = request.user
        if appointment.doctor.user != user:
            raise PermissionDenied("You do not have permission to complete this appointment.")

        if appointment.status == AppointmentStatus.CANCELED:
            raise ValidationError({"status": "Cannot complete a canceled appointment."})

        if appointment.status == AppointmentStatus.COMPLETED:
            raise ValidationError({"status": "This appointment is already completed."})

        if appointment.time_slot.schedule.work_date > timezone.now().date():
            raise ValidationError({"status": "Cannot complete an appointment that is scheduled for a future date."})

        with transaction.atomic():
            appointment.status = AppointmentStatus.COMPLETED
            appointment.save(update_fields=['status'])

        return Response(
            {"detail": "Appointment marked as completed successfully.", 
             "status": appointment.status},
            status=status.HTTP_200_OK
        )
    
    @action(methods=['post'], detail=False, url_path='book-for-patient')
    def book_for_patient(self, request):
        serializer = ReceptionistBookSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # create appointment
        appointment = serializer.save()

        return Response({
            "message": "Booked successfully",
            "data": AppointmentSerializer(appointment).data
        }, status=201)
    
    @action(methods=['get'], detail=False, url_path='dashboard', permission_classes=[IsReceptionist])
    def dashboard(self, request):
        today = timezone.localdate()
        # today = "2026-04-18"
        # print(today)

        queryset = get_base_queryset().filter(
            work_date=today
        ).order_by('slot_time')

        total = queryset.count()
        completed = queryset.filter(status=AppointmentStatus.COMPLETED).count()
        waiting = queryset.filter(status=AppointmentStatus.BOOKED).count()
        canceled = queryset.filter(status=AppointmentStatus.CANCELED).count()

        serializer = AppointmentSerializer(queryset, many=True)

        return Response({
            "total": total,
            "completed": completed,
            "waiting": waiting,
            "canceled": canceled,
            "results": serializer.data
        })