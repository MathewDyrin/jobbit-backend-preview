from rest_framework.pagination import PageNumberPagination


class ChatsListPagination(PageNumberPagination):
    page_size = 15


class ChatHistoryPagination(PageNumberPagination):
    page_size = 10


class ChatParticipantsPagination(PageNumberPagination):
    page_size = 20
