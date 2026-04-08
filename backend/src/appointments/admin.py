from django.contrib import admin
from .models import Appointment

class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'patient', 'doctor', 'time_slot', 'status']
    search_fields = ['patient__user__username', 'doctor__user__username']
    list_filter = ['status', 'time_slot__schedule__work_date']

admin.site.register(Appointment, AppointmentAdmin)