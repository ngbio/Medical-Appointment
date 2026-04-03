from rest_framework.pagination import CursorPagination

class DoctorProfileCursorPagination(CursorPagination):
    page_size = 9
    ordering = 'specialty_id'

class SpecialtyCursorPagination(CursorPagination):
    page_size = 5
    ordering = 'id'
