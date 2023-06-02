from rest_framework import serializers
from . import models
from executor.serializers import ExecutorProfileSerializer
from client.serializers import ClientProfileSerializer


class OrderSpecificSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    text = serializers.CharField(max_length=1024)


class CreateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.OrderModel
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    client = ClientProfileSerializer(read_only=True)
    executor = ExecutorProfileSerializer(read_only=True)
    specifics = OrderSpecificSerializer(many=True, read_only=True)

    class Meta:
        model = models.OrderModel
        fields = '__all__'
