from rest_framework.permissions import IsAuthenticated

class IsDoctor(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return super().has_object_permission(request, view, obj) and request.user.role == 'doctor'
