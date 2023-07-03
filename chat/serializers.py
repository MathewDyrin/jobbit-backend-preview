from urllib import request
from rest_framework import serializers

from order.serializers import OrderSerializer
from user.serializers import UserSerializer
from . import models


class ChatFileSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField()
    media_type = serializers.SerializerMethodField()

    class Meta:
        model = models.ChatFileModel
        fields = '__all__'

    @staticmethod
    def get_url_headers(url: str) -> dict:
        req = request.Request(url, method='HEAD')
        f = request.urlopen(req)
        return f.headers

    def get_name(self, obj):
        return obj.file_url.split('/')[-1]

    def get_size(self, obj):
        return self.get_url_headers(obj.file_url)['Content-Length']

    def get_media_type(self, obj):
        return self.get_url_headers(obj.file_url)['Content-Type']


class CreateParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ParticipantModel
        fields = '__all__'


class ParticipantSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = models.ParticipantModel
        fields = '__all__'


class CreateMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.MessageModel
        fields = '__all__'


class AnswerSerializer(serializers.ModelSerializer):
    author = ParticipantSerializer(read_only=True)
    files = ChatFileSerializer(read_only=True, many=True)

    class Meta:
        model = models.MessageModel
        fields = '__all__'


class MessageSerializer(serializers.ModelSerializer):
    author = ParticipantSerializer(read_only=True)
    files = ChatFileSerializer(read_only=True, many=True)
    answer = AnswerSerializer(read_only=True)

    class Meta:
        model = models.MessageModel
        fields = '__all__'


class CreateChatSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(choices=models.ParticipantModel.ParticipantRoles.choices)
    order_id = serializers.IntegerField()
    executor = serializers.UUIDField(required=False)

    class Meta:
        model = models.ChatModel
        fields = '__all__'


class ChatSerializer(serializers.ModelSerializer):
    participants = ParticipantSerializer(read_only=True, many=True)
    associated_order = OrderSerializer(read_only=True)
    last_message = serializers.SerializerMethodField()
    unreaded_message = serializers.SerializerMethodField()

    class Meta:
        model = models.ChatModel
        exclude = ('messages',)

    def get_last_message(self, obj):
        if message := obj.messages.order_by('-created_time').first():
            return MessageSerializer(instance=message).data
        return None

    def get_unreaded_message(self, obj):
        request = self.context['request']
        return obj.messages.filter(status=models.MessageModel.MessageStatus.NOT_READ) \
            .exclude(author__user=request.user) \
            .count()
