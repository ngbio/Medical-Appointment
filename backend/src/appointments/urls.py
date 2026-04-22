from django.urls import path, include
from users.views import user_views
from rest_framework.routers import DefaultRouter
from appointments.views.appointment_view import AppointmentViewSet
r = DefaultRouter()
r.register('appointments',AppointmentViewSet, basename='appointment')

urlpatterns = [
    path('', include(r.urls)),
]