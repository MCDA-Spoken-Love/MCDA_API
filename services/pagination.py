from rest_framework.pagination import CursorPagination


class CursorPagination(CursorPagination):
    # Three records will be shown per page
    page_size = 50
    # Ordering the records
    ordering = 'timestamp'
