from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import NotFound

from users.models import PatientProfile
from users.serializers.patient_serializers import PatientProfileSerializer
from src.perms import IsPatient

class PatientProfileViewSet(viewsets.GenericViewSet):
    serializer_class = PatientProfileSerializer
    permission_classes = [IsPatient]

    def get_object(self):
        try:
            return self.request.user.patient_profile
        except PatientProfile.DoesNotExist:
            raise NotFound("Patient profile not found.")

    @action(methods=['get', 'put', 'patch'], detail=False, url_path='me')
    def me(self, request):
        profile = self.get_object()

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