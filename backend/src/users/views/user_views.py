from django.shortcuts import render
from rest_framework import viewsets, permissions, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from users.models import User
from users.serializers.user_serializers import UserSerializer
from users.paginators import UserCursorPagination
from django.contrib.auth import logout
from django.shortcuts import redirect
from src.perms import IsAdmin
from django.contrib.auth import authenticate, login


# Create your views here.
class UserView(viewsets.GenericViewSet,
               mixins.CreateModelMixin):
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    pagination_class = UserCursorPagination

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [IsAdmin]

        return [permission() for permission in permission_classes]

    @action(methods=['get', 'patch'], detail=False, permission_classes=[permissions.IsAuthenticated],
            url_path='current-user')
    def current_user(self, request):
        user = request.user

        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data)

        if request.method == 'PATCH':
            serializer = self.get_serializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(serializer.data)

def redirect_user_by_role(user):

    # Doctor
    if hasattr(user, "doctor_profile"):
        return redirect("/doctor/dashboard/")

    # Patient
    if hasattr(user, "patient_profile"):
        return redirect("/booking/")

    # Admin
    if user.is_staff or user.is_superuser:
        return redirect("/admin/")

    # fallback
    return redirect("/index")

def login_page(request):
    if request.method == "GET":
        return render(request, "auth/login.html")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is None:
            return render(request, "auth/login.html", {
                "error": "Invalid username or password"
            })

        # Login success
        login(request, user)

        # Redirect by role
        return redirect_user_by_role(user)


def register_page(request):
    return render(request, "auth/register.html")

def booking_page(request):
    return render(request, "appointment/booking.html")

def infor_users(request):
    return render(request, "auth/infor_user.html")


def logout_view(request):
    """Handle logout and redirect to login page"""
    logout(request)
    return redirect('/login')

def index_page(request):
    return render(request, "index.html")

