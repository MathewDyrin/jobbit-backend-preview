from rest_framework import serializers

from order.serializers import FileSerializer, UserSerializer, FactorySerializer
from . import models


class CreateAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AnswerModel
        fields = '__all__'


class AnswerSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    files = FileSerializer(read_only=True, many=True)

    class Meta:
        model = models.AnswerModel
        fields = '__all__'


class FeedbackSerializer(serializers.ModelSerializer):
    author_user = UserSerializer(read_only=True)
    author_factory = FactorySerializer(read_only=True)
    answers = AnswerSerializer(read_only=True, many=True)
    on_user = UserSerializer(read_only=True)
    on_factory = FactorySerializer(read_only=True)
    files = FileSerializer(read_only=True, many=True)

    class Meta:
        model = models.FeedbackModel
        fields = '__all__'


class CreateFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FeedbackModel
        fields = '__all__'
