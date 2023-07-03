from rest_framework.pagination import PageNumberPagination


class TransactionsListPagination(PageNumberPagination):
    page_size = 20
