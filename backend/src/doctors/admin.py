from django.contrib import admin

from doctors.models import DoctorProfile, Specialty

class DoctorAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_id', 'experience_years', 'specialty']
    search_fields = ['specialty']
    list_filter = ['specialty']

class SpecialtyAdmin(admin.ModelAdmin):
    list_display = ['name']

admin.site.register(DoctorProfile, DoctorAdmin)
admin.site.register(Specialty, SpecialtyAdmin)
