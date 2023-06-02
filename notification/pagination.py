from rest_framework.pagination import PageNumberPagination


class NotificationsListPagination(PageNumberPagination):
    page_size = 20
