from django.urls import path, include

from .views.receptionist_view import book_for_patient, dashboard
from users.views.patient_views import patient_list, patient_detail

urlpatterns = [
    path('receptionist/book-for-patient/', book_for_patient, name='book_for_patient'),
    path('receptionist/dashboard/', dashboard, name='receptionist_dashboard'),
    path('receptionist/patient-list/', patient_list, name='receptionist_patient_list'),
    path('receptionist/patient/<int:patient_id>/', patient_detail, name='receptionist_patient_detail'),

]
