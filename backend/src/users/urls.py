from django.urls import path, include
from users import views
from rest_framework.routers import DefaultRouter

r = DefaultRouter()
r.register('users', views.UserView, basename='user')

urlpatterns = [
    path('', include(r.urls)),
]
