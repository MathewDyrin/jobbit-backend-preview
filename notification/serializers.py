from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'


class NotificationReadSerializer(serializers.Serializer):
    id = serializers.CharField(max_length=500)
