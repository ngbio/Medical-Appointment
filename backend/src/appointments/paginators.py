from rest_framework.pagination import CursorPagination

class AppointmentsPagination(CursorPagination):
    page_size = 2
    ordering = (
        'work_date',
        'slot_time',
        'id'
    )
