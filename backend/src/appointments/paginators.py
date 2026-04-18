from rest_framework.pagination import CursorPagination

class AppointmentsPagination(CursorPagination):
    page_size = 2
    ordering = (
        'time_slot__schedule__work_date',
        'time_slot__start_time',
        'id'
    )
