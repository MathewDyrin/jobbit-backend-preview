from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from django.core.exceptions import ObjectDoesNotExist

from . import permissions, serializers, pagination, models


class CreateClientVerificationView(generics.CreateAPIView):
    permission_classes = (permissions.IsUserProfile,)
    serializer_class = serializers.CreateClientVerificationSerializer

    def post(self, request, *args, **kwargs):
        response = dict()
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            new_client_verification = serializer.create(serializer.validated_data)
            response.update(self.get_serializer(instance=new_client_verification).data)
            return Response(response, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ClientFeedbackViewSet(pagination.ClientFeedbackPagination, viewsets.ModelViewSet):
    serializer_class = serializers.ClientFeedbackSerializer
    permission_classes_per_action = {
        'list': (permissions.ClientFeedbackPermission,),
        'retrieve': (permissions.ClientFeedbackPermission,),
        'partial_update': (permissions.ClientFeedbackPermission,),
        'destroy': (permissions.ClientFeedbackPermission,),
        'answer': (permissions.IsAllowToAnswerFeedback,),
    }

    def get_serializer_class(self):
        if self.action == 'create':
            return serializers.CreateClientFeedbackSerializer
        if self.action == 'answer':
            return serializers.AnswerOnFeedbackSerializer
        return super().get_serializer_class()

    def get_queryset(self, client_profile=None, feedback_id=None):
        if self.action == 'list':
            return client_profile.client_feedbacks.all()
        if self.action in ['retrieve', 'answer', 'partial_update', 'destroy']:
            return client_profile.client_feedbacks.get(id=feedback_id)

    def list(self, request, *args, **kwargs):
        try:
            client_profile = models.ClientProfileModel.objects.get(id=kwargs['client_id'])
            qs = self.paginate_queryset(
                self.get_queryset(client_profile=client_profile),
                request=request,
                view=self
            )
            data = self.get_serializer(qs, many=True).data
            return self.get_paginated_response(data)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def retrieve(self, request, *args, **kwargs):
        try:
            client_profile = models.ClientProfileModel.objects.get(id=kwargs['client_id'])
            qs = self.get_queryset(client_profile=client_profile,
                                   feedback_id=kwargs['pk'])
            data = self.get_serializer(qs).data
            return Response(data, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def partial_update(self, request, *args, **kwargs):
        try:
            client_profile = models.ClientProfileModel.objects.get(id=kwargs['client_id'])
            serializer = self.get_serializer(
                self.get_queryset(client_profile=client_profile,
                                  feedback_id=kwargs['pk']),
                data=request.data,
                partial=True
            )

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, *args, **kwargs):
        try:
            client_profile = models.ClientProfileModel.objects.get(id=kwargs['client_id'])
            self.get_queryset(client_profile=client_profile,
                              feedback_id=kwargs['pk']).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @action(methods=['POST'], detail=True)
    def answer(self, request, *args, **kwargs):
        try:
            client_profile = models.ClientProfileModel.objects.get(id=kwargs['client_id'])
            qs = self.get_queryset(client_profile=client_profile,
                                   feedback_id=kwargs['pk'])
            serializer = self.get_serializer(qs, request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class ClientProfileViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ClientProfileSerializer
    permission_classes = (permissions.ClientProfilePermission,)
    queryset = models.ClientProfileModel.objects.all()
    pagination_class = pagination.PageNumberPagination

    def get_serializer_class(self):
        if self.action == 'create':
            return serializers.CreateClientProfileSerializer
        return super().get_serializer_class()
