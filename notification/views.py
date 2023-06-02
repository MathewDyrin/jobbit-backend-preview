from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework import viewsets
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist
from .pagination import NotificationsListPagination
from . import serializers
from . import models


User = get_user_model()


class NotificationView(mixins.ListModelMixin,
                       mixins.RetrieveModelMixin,
                       NotificationsListPagination,
                       viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = models.Notification.objects.filter(user=request.user)
        results = self.paginate_queryset(queryset, request, view=self)
        serializer = serializers.NotificationSerializer(results, many=True)

        for item in serializer.data:
            item['icon'] = request.build_absolute_uri(item['icon'])

        return self.get_paginated_response(serializer.data)

    @action(detail=False, methods=['POST'])
    def read(self, request, *args, **kwargs):
        serializer = serializers.NotificationReadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            row = models.Notification.objects.get(pk=serializer.validated_data['id'])
            if row.user != request.user:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            if row.status == models.NotificationStatus.UNREAD:
                row.status = models.NotificationStatus.READ
                row.save()
            return Response(status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'])
    def read_all(self, request, *args, **kwargs):
        notifications = models.Notification.objects.filter(user=request.user)
        for item in notifications:
            if item.status == models.NotificationStatus.UNREAD:
                item.status = models.NotificationStatus.READ
                item.save()
        return Response(status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'])
    def check(self, request):
        unread_notifications = models.Notification.objects.filter(user=request.user).filter(
            status=models.NotificationStatus.UNREAD).all()
        return Response({'count': len(unread_notifications)}, status=status.HTTP_200_OK)
