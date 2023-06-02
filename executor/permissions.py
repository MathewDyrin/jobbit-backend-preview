from rest_framework.permissions import IsAuthenticated

from .models import ExecutorProfileModel
from client.models import ClientProfileModel


class IsUserProfile(IsAuthenticated):
    def has_permission(self, request, view):
        if ExecutorProfileModel.objects.filter(user_id=request.user.id):
            return True
        return False


class ExecutorProfilePermission(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        if view.action in ['list', 'retrieve']:
            return True
        if view.action == 'create':
            return True
        if view.action in ['update', 'partial_update']:
            return obj.executor_profile.user_id == request.user.id
        if view.action == 'destroy':
            return obj.executor_profile.user_id == request.user.id


class ExecutorFeedbackPermission(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        if view.action in ['list', 'retrieve']:
            return True
        if view.action == 'create':
            if ClientProfileModel.objects.filter(user_id=request.user.id):
                return True
            return False
        if view.action in ['update', 'partial_update']:
            return obj.executor_profile.user_id == request.user.id
        if view.action == 'destroy':
            return request.user.is_superuser


class IsAllowToAnswerFeedback(IsAuthenticated):
    def has_permission(self, request, view):
        if view.action == 'answer':
            return True
        return False
