from django.urls import path, include
from users.views import user_views
from rest_framework.routers import DefaultRouter
from users.views.user_views import login_page, index_page, infor_users, register_page, booking_page, my_appointment_page, doctor_list_page
from users.views.patient_views import PatientProfileViewSet

r = DefaultRouter()
r.register('users', user_views.UserView, basename='user')
r.register('patients', PatientProfileViewSet , basename='patient')

urlpatterns = [
    path('', include(r.urls)),
    path('index/', index_page, name='index'),
    path('login/', login_page, name='login'),
    path('register/', register_page, name='register'),
    path('booking/', booking_page, name='booking'),
    path('logout/', user_views.logout_view, name='logout'),
    path('infor_user/', infor_users, name='infor_user'),
    path('my_appointments/', my_appointment_page, name='my_appointments'),
    path('doctor_list/', doctor_list_page, name='doctor_list'),
]
