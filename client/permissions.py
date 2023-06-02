from rest_framework.permissions import IsAuthenticated

from .models import ClientProfileModel
from executor.models import ExecutorProfileModel


class IsUserProfile(IsAuthenticated):
    def has_permission(self, request, view):
        if ClientProfileModel.objects.filter(user_id=request.user.id):
            return True
        return False


class ClientProfilePermission(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        if view.action in ['list', 'retrieve']:
            return True
        if view.action == 'create':
            return True
        if view.action in ['update', 'partial_update']:
            return obj.user_id == request.user.id
        if view.action == 'destroy':
            return obj.user_id == request.user.id


class ClientFeedbackPermission(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        if view.action in ['list', 'retrieve']:
            return True
        if view.action == 'create':
            if ExecutorProfileModel.objects.filter(user_id=request.user.id):
                return True
            return False
        if view.action in ['update', 'partial_update']:
            return obj.author.user_id == request.user.id
        if view.action == 'destroy':
            return request.user.is_superuser


class IsAllowToAnswerFeedback(IsAuthenticated):
    def has_permission(self, request, view):
        if view.action == 'answer':
            return True
        return False
