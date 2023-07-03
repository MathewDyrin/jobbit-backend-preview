from rest_framework.exceptions import APIException
from rest_framework import status
from django.utils.translation import gettext_lazy as _


class ChatAlreadyExist(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('Chat is already exists')


class ChatByResponseAlreadyExist(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('Chat for this response is already exists')
