from django.urls import path, include
from .views.doctor_view import DoctorProfileViewSet
from .views.specialty_view import SpecialtyViewSet

from rest_framework.routers import DefaultRouter

r = DefaultRouter()
r.register('doctors', DoctorProfileViewSet, basename='doctor')
r.register('specialties', SpecialtyViewSet, basename='specialty')
urlpatterns = [
    path('', include(r.urls)),
]
