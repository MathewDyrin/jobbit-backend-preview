from rest_framework import permissions


class CurrentUser(permissions.IsAuthenticated):

    def has_object_permission(self, request, view, obj):
        return obj.pk == request.user.pk


class StaffMemberOrSuperuser(permissions.IsAuthenticated):

    def has_object_permission(self, request, view, obj):
        return request.user.is_staff_member or request.user.is_superuser
