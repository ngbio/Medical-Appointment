from django.contrib import admin

from doctors.models import DoctorProfile, Specialty, DoctorSchedule, TimeSlot

class DoctorAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_id', 'experience_years', 'specialty']
    search_fields = ['specialty']
    list_filter = ['specialty']

class SpecialtyAdmin(admin.ModelAdmin):
    list_display = ['name']

class ScheduleAdmin(admin.ModelAdmin):
    list_display = ['id', 'doctor', 'work_date', 'start_time', 'end_time']
    search_fields = ['doctor']

class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ['id', 'start_time', 'end_time', 'status', 'schedule_id']

admin.site.register(DoctorProfile, DoctorAdmin)
admin.site.register(Specialty, SpecialtyAdmin)
admin.site.register(DoctorSchedule, ScheduleAdmin)
admin.site.register(TimeSlot, TimeSlotAdmin)
