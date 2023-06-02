from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status, mixins, viewsets, permissions as drf_permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from . import models, serializers
from order.services import add_files_to_obj


class FeedbackViewSet(mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin,
                      viewsets.GenericViewSet):
    serializer_class = serializers.FeedbackSerializer
    permission_classes = (drf_permissions.IsAuthenticatedOrReadOnly,)
    queryset = models.FeedbackModel.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return serializers.CreateFeedbackSerializer
        if self.action == 'answer':
            return serializers.CreateAnswerSerializer
        else:
            return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        response = dict()
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            new_feedback = serializer.create(serializer.validated_data)
            new_feedback.author_user = request.user
            if request.data.get('files_url'):
                add_files_to_obj(new_feedback, request.data['files_url'])
            new_feedback.save()
            response.update(self.get_serializer(instance=new_feedback).data)
            return Response(response, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['POST'], detail=True)
    def answer(self, request, *args, **kwargs):
        response = dict()
        try:
            feedback = models.FeedbackModel.objects.get(pk=kwargs['pk'])
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                new_answer = serializer.create(serializer.validated_data)
                new_answer.author = request.user
                if request.data.get('files_url'):
                    add_files_to_obj(new_answer, request.data['files_url'])
                new_answer.save()
                feedback.answers.add(new_answer)
                response.update(self.get_serializer(instance=new_answer).data)
                return Response(response, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
