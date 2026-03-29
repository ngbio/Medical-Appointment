from django.urls import path, include
from .views.user_views import UserView
from rest_framework.routers import DefaultRouter

r = DefaultRouter()
r.register('users', UserView, basename='user')
urlpatterns = [
    path('', include(r.urls)),
]
