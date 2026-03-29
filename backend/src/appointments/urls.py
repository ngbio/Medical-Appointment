from rest_framework.routers import DefaultRouter
from django.urls import path, include
from . import views

r = DefaultRouter()
r.register('appointments', views.AppointmentViewSet, basename='appointment')
urlpatterns = [
    path('', include(r.urls)),
]