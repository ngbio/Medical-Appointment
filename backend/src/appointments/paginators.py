from rest_framework.pagination import CursorPagination

class AppointmentsPagination(CursorPagination):
    page_size = 6
    ordering= 'created_at'
