from django.urls import path, include

from .views.doctor_view import DoctorProfileViewSet, doctor_schedule, doctor_examination_detail, doctor_examination_list
from .views.specialty_view import SpecialtyViewSet
from .views.schedule_view import ScheduleViewSet
from users.views.patient_views import patient_list, patient_detail

from rest_framework.routers import DefaultRouter

r = DefaultRouter()
r.register('doctors', DoctorProfileViewSet, basename='doctor')
r.register('specialties', SpecialtyViewSet, basename='specialty')
r.register('schedules', ScheduleViewSet, basename='schedule')
urlpatterns = [
    path('', include(r.urls)),
    path('doctor/schedule', doctor_schedule, name='doctor_schedule'),
    path('doctor/examination/<int:appointment_id>', doctor_examination_detail, name='doctor_examination_detail'),
    path('doctor/examination-list', doctor_examination_list, name='doctor_examination_list'),
    path('doctor/patient-list', patient_list, name='doctor_patient_list'),
    path('doctor/patient/<int:patient_id>', patient_detail, name='doctor_patient_detail'),
]
