
from rest_framework import viewsets, parsers, permissions, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from django.db.models import Q
from django.shortcuts import render

from users.models import PatientProfile, RoleEnum
from users.serializers.patient_serializers import PatientProfileSerializer
from src.perms import IsPatient
from appointments.models import Appointment
from appointments.serializers.appointment_serializers import AppointmentSerializer
from users.paginators import PatientProfilePagination
from appointments.services.query_service import get_base_queryset

class PatientProfileViewSet(viewsets.GenericViewSet,
                            mixins.RetrieveModelMixin,
                            mixins.ListModelMixin):
    serializer_class = PatientProfileSerializer
    pagination_class = PatientProfilePagination
    # permission_classes = [IsPatient]
    queryset = PatientProfile.objects.select_related("user")

    def get_permissions(self):
        if self.action == 'appointments':
            return [permissions.IsAuthenticated()]
        if self.action == 'me':
            return [permissions.IsAuthenticated(), IsPatient()]
        
        return [permissions.IsAuthenticated()]

    def get_object(self):
        pk = self.kwargs.get("pk")

        try:
            return PatientProfile.objects.select_related("user").get(pk=pk)
        except PatientProfile.DoesNotExist:
            raise NotFound("Patient not found.")

    def get_queryset(self):
        queryset = self.queryset

        user = self.request.user

        if not user.is_authenticated:
            return PatientProfile.objects.none()

        if user.role == RoleEnum.PATIENT: # Patient can only see their own profile
            return queryset.filter(user=user)

        # Search
        query = self.request.query_params.get("q")

        if query:
            queryset = queryset.filter(
                Q(user__fullname__icontains=query) |
                Q(address__icontains=query) |
                Q(user__phone_number__icontains=query)
            )

        dob = self.request.query_params.get("dob")
        if dob:
            queryset = queryset.filter(dob=dob)

        return queryset

    @action(methods=['get', 'patch'], detail=False, url_path='me')
    def me(self, request):
        try:
            profile = PatientProfile.objects.select_related("user").get(
                user=request.user
            )
        except PatientProfile.DoesNotExist:
            raise NotFound("Patient profile not found.")

        if request.method == 'GET':
            serializer = self.get_serializer(profile)
            return Response(serializer.data)

        serializer = self.get_serializer(
            profile,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(methods=['get'], detail=True, url_path='appointments')
    def appointments(self, request, pk=None):
        patient = self.get_object()

        appointments = get_base_queryset().filter(
            patient=patient
        ).order_by("-work_date")

        serializer = AppointmentSerializer(appointments, many=True)

        return Response({
            "patient": PatientProfileSerializer(patient).data,
            "appointments": serializer.data
        })
    
def patient_list(request):
    # print(request.user)
    return render(request, "patient/patient_list.html")

def patient_detail(request, patient_id):
    return render(request, "patient/patient_detail.html", {"patient_id": patient_id})