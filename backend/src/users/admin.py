from django.contrib import admin
from users.models import User
from django.urls import path
from django.template.response import TemplateResponse


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'role', 'is_active')


class MyAdminSite(admin.AdminSite):
    site_header = 'User Management'


admin_site = MyAdminSite(name='User Admin')

admin_site.register(User)