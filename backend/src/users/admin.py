from django.contrib import admin

from users.models import User, PatientProfile
from django.urls import path
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User

    list_display = ['id', 'username', 'email', 'role', 'is_active']
    search_fields = ['username', 'email']
    list_filter = ['role', 'is_active']

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Thông tin cá nhân', {
            'fields': ('first_name', 'last_name', 'fullname', 'email', 'gender')
        }),
        ('Phân quyền', {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser')
        }),
    )


    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role'),
        }),
    )

    ordering = ['id']

class MyAdminSite(admin.AdminSite):
    site_header = 'User Management'


class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'dob', 'address']
    list_filter = ['id']

admin_site = MyAdminSite(name='User Admin')

# admin_site.register(User)
admin.site.register(PatientProfile, PatientProfileAdmin)
