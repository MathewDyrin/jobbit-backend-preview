from rest_framework.pagination import PageNumberPagination


class ExecutorFeedbackPagination(PageNumberPagination):
    page_size = 35


class ExecutorAddressPagination(PageNumberPagination):
    page_size = 35


class ExecutorGeoPagination(PageNumberPagination):
    page_size = 35


class ExecutorPortfolioPagination(PageNumberPagination):
    page_size = 35


class ExecutorServicePagination(PageNumberPagination):
    page_size = 35


class ExecutorExperiencePagination(PageNumberPagination):
    page_size = 35
