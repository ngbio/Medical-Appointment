from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from appointments.models import Appointment, AppointmentStatus
from appointments.serializers.appointment_serializers import AppointmentSerializer
from users.models import RoleEnum
from appointments.paginators import AppointmentsPagination
from doctors.models import SlotStatus
from rest_framework import permissions
from src.perms import IsPatient
from src.perms import IsAdmin
from doctors.perms import IsDoctor
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

        if self.action in ['list', 'retrieve', 'cancel_appointment']:
            return [(IsPatient | IsAdmin | IsDoctor)()]

        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Appointment.objects.none()

        # Queryset cơ bản với select_related để tối ưu
        queryset = Appointment.objects.select_related(
            'doctor__user', 'patient__user', 'time_slot__schedule'
        ).order_by('-time_slot__schedule__work_date', '-time_slot__start_time')


        query_params = self.request.query_params
        status_param = query_params.get('status')
        from_date = query_params.get('from')
        to_date = query_params.get('to')

        if status_param:
            queryset = queryset.filter(status=status_param)
        if from_date and to_date:
            queryset = queryset.filter(
                time_slot__schedule__work_date__range=[from_date, to_date]
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

