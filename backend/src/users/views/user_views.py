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


def login_page(request):
    return render(request, "auth/login.html")

def register_page(request):
    return render(request, "auth/register.html")

def booking_page(request):
    return render(request, "appointment/booking.html")

def infor_users(request):
    return render(request, "auth/nfor_user.html")


def logout_view(request):
    """Handle logout and redirect to login page"""
    logout(request)
    return redirect('/login')

def index_page(request):
    return render(request, "index.html")

