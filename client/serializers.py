from abc import ABC

from rest_framework import serializers

from . import models
from user.serializers import UserSerializer


class CreateClientProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ClientProfileModel
        fields = '__all__'
        read_only_fields = ('is_verified', 'created_date')


class ClientProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = models.ClientProfileModel
        fields = '__all__'
        read_only_fields = ('is_verified', 'created_date')


class CreateClientVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ClientVerificationModel
        fields = '__all__'


class ClientVerificationSerializer(serializers.ModelSerializer):
    client = ClientProfileSerializer(read_only=True)

    class Meta:
        model = models.ClientVerificationModel
        fields = '__all__'


class CreateClientFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ClientFeedbackModel
        fields = '__all__'
        read_only_fields = ('answer',)


class ClientFeedbackSerializer(serializers.ModelSerializer):
    client_profile = ClientProfileSerializer(read_only=True)

    class Meta:
        model = models.ClientFeedbackModel
        fields = '__all__'
        read_only_fields = ('answer',)


class AnswerOnFeedbackSerializer(serializers.ModelSerializer):
    client_profile = ClientProfileSerializer(read_only=True)

    class Meta:
        model = models.ClientFeedbackModel
        fields = '__all__'
