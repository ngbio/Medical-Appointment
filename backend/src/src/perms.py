from rest_framework.permissions import IsAuthenticated
from users.models import RoleEnum

class IsOwner(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return super().has_object_permission(request, view, obj) and obj.user == request.user

class IsAdmin(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return super().has_object_permission(request, view, obj) and request.user.role == 'admin'
class IsPatient(IsAuthenticated):
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.role == RoleEnum.PATIENT
        )