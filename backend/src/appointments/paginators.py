from rest_framework import pagination


class AppointmentsPaginator(pagination.PageNumberPagination):
    page_size = 6