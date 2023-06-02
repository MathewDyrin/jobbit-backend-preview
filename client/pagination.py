from rest_framework.pagination import PageNumberPagination


class ClientFeedbackPagination(PageNumberPagination):
    page_size = 35
