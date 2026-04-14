from rest_framework.pagination import CursorPagination

class AppointmentsPagination(CursorPagination):
    page_size = 2
    ordering= 'created_at'
