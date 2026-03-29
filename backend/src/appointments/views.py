# views.py
from rest_framework import viewsets, generics, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.mixins import ListModelMixin, CreateModelMixin, RetrieveModelMixin
from .models import Appointment, AppointmentStatus
from . import serializers, paginators
from doctors.models import SlotStatus
from patients.permissions import IsPatient


class AppointmentViewSet(viewsets.GenericViewSet,ListModelMixin,CreateModelMixin,RetrieveModelMixin):
    serializer_class = serializers.AppointmentSerializer
    permission_classes = [IsPatient]
    pagination_class = paginators.AppointmentsPaginator  # fix typo

    def get_queryset(self):
        profile = self.request.user.patient_profile
        return Appointment.objects.filter(patient=profile).select_related(
            'doctor__user', 'patient__user', 'time_slot__schedule'
        )

    def perform_create(self, serializer):
        profile = self.request.user.patient_profile
        serializer.save(patient=profile)

    @action(methods=['patch'], detail=True, url_path='cancel')
    def cancel_appointment(self, request, pk=None):
        appointment = self.get_object()

        if appointment.status == AppointmentStatus.CANCELED:
            return Response({"detail": "Lịch hẹn đã bị hủy trước đó."}, status=status.HTTP_400_BAD_REQUEST)

        if appointment.status == AppointmentStatus.COMPLETED:
            return Response({"detail": "Không thể hủy lịch khám đã hoàn thành."}, status=status.HTTP_400_BAD_REQUEST)

        appointment.status = AppointmentStatus.CANCELED
        appointment.save()

        if appointment.time_slot:
            appointment.time_slot.status = SlotStatus.AVAILABLE
            appointment.time_slot.save()

        return Response({"detail": "Hủy lịch hẹn thành công."}, status=status.HTTP_200_OK)