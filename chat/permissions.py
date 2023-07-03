from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied


class IsMessageAuthor(IsAuthenticated):
    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        if view.action in ['partial_update', 'update', 'destroy']:
            return obj.author.user.id == request.user.id
        return True


class IsAdmin(IsAuthenticated):
    def has_permission(self, request, view):
        if view.action in ['create', 'destroy']:
            return request.user.is_admin
        return True

    def has_object_permission(self, request, view, obj):
        if view.action in ['create', 'destroy']:
            return request.user.is_admin
        return True


def is_chat_participant(chat, user, role):
    if not chat.participants.filter(user=user).filter(role=role).exists():
        raise PermissionDenied
