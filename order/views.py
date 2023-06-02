from rest_framework import viewsets

from . import models, serializers, pagination


class OrderViewSet(viewsets.ModelViewSet):
    queryset = models.OrderModel.objects.all()
    serializer_class = serializers.OrderSerializer
    pagination_class = pagination.OrderPagination

    def get_serializer_class(self):
        if self.action in ['create', 'partial_update', 'update']:
            return serializers.CreateOrderSerializer
        return super().get_serializer_class()
