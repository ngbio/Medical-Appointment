from django.shortcuts import render, redirect
from rest_framework import viewsets, generics, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import logout

from users.models import User
from users import serializers


# Create your views here.
class UserView(viewsets.ViewSet, generics.CreateAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = serializers.UserSerializer

    @action(methods=['get', 'patch'], url_path='current-user', detail=False,
            permission_classes=[permissions.IsAuthenticated])
    def get_current_user(self, request):
        u = request.user

        if request.method == 'PATCH':
            for k, v in request.data.items():
                if k in ['first_name', 'last_name', 'email']:
                    setattr(u, k, v)
            u.save()

        return Response(
            serializers.UserSerializer(u).data,
            status=status.HTTP_200_OK
        )


def login_page(request):
    return render(request, "index.html")


def logout_view(request):
    """Handle logout and redirect to login page"""
    logout(request)
    return redirect('/login')


def index_page(request):
    return render(request, "index.html")