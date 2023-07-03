from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist
from django_filters.rest_framework import DjangoFilterBackend

from . import permissions, serializers, models, pagination, filters


class CreateExecutorVerificationView(generics.CreateAPIView):
    permission_classes = (permissions.IsUserProfile,)
    serializer_class = serializers.CreateExecutorVerificationSerializer

    def post(self, request, *args, **kwargs):
        response = dict()
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            new_executor_verification = serializer.create(
                serializer.validated_data)
            response.update(self.get_serializer(instance=new_executor_verification).data)
            return Response(response, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ExecutorFeedbackViewSet(pagination.ExecutorFeedbackPagination, viewsets.ModelViewSet):
    permission_classes = (permissions.ExecutorFeedbackPermission,
                          permissions.IsAllowToAnswerFeedback)
    serializer_class = serializers.ExecutorFeedbackSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return serializers.CreateExecutorFeedbackSerializer
        if self.action == 'answer':
            return serializers.AnswerOnFeedbackSerializer
        return super().get_serializer_class()

    def get_queryset(self, executor_profile=None, feedback_id=None):
        if self.action == 'list':
            return executor_profile.executor_feedbacks.all()
        if self.action in ['retrieve', 'answer', 'partial_update', 'destroy']:
            return executor_profile.executor_feedbacks.get(id=feedback_id)

    def list(self, request, *args, **kwargs):
        try:
            executor_profile = models.ExecutorProfileModel.objects.get(
                id=kwargs['executor_id'])
            qs = self.paginate_queryset(
                self.get_queryset(executor_profile=executor_profile),
                request=request,
                view=self
            )
            data = self.get_serializer(qs, many=True).data
            return self.get_paginated_response(data)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def retrieve(self, request, *args, **kwargs):
        try:
            executor_profile = models.ExecutorProfileModel.objects.get(
                id=kwargs['executor_id'])
            qs = self.get_queryset(executor_profile=executor_profile,
                                   feedback_id=kwargs['pk'])
            data = self.get_serializer(qs).data
            return Response(data, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def partial_update(self, request, *args, **kwargs):
        try:
            executor_profile = models.ExecutorProfileModel.objects.get(
                id=kwargs['executor_id'])
            serializer = self.get_serializer(
                self.get_queryset(executor_profile=executor_profile,
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
            executor_profile = models.ExecutorProfileModel.objects.get(
                id=kwargs['executor_id'])
            self.get_queryset(executor_profile=executor_profile,
                              feedback_id=kwargs['pk']).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @action(methods=['POST'], detail=True)
    def answer(self, request, *args, **kwargs):
        try:
            executor_profile = models.ExecutorProfileModel.objects.get(
                id=kwargs['executor_id'])
            qs = self.get_queryset(executor_profile=executor_profile,
                                   feedback_id=kwargs['pk'])
            serializer = self.get_serializer(qs, request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class ExecutorProfileViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ExecutorProfileSerializer
    permission_classes = (permissions.ExecutorProfilePermission,)
    queryset = models.ExecutorProfileModel.objects.all()
    pagination_class = pagination.PageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = filters.ExecutorFilters

    def get_serializer_class(self):
        if self.action == 'create':
            return serializers.CreateExecutorProfileSerializer
        return super().get_serializer_class()


class ExecutorAddressViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ExecutorAddressSerializer
    permission_classes = (permissions.IsUserProfile,)
    queryset = models.ExecutorAddressModel.objects.all()
    pagination_class = pagination.ExecutorAddressPagination

    def get_serializer_class(self):
        if self.action == 'create':
            return serializers.CreateExecutorAddressSerializer
        return super().get_serializer_class()


class ExecutorGeoViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ExecutorGeoSerializer
    permission_classes = (permissions.ExecutorProfilePermission,)
    queryset = models.ExecutorGeoModel.objects.all()
    pagination_class = pagination.ExecutorGeoPagination

    def get_serializer_class(self):
        if self.action in ['create', 'partial_update', 'update']:
            return serializers.CreateExecutorGeoSerializer
        return super().get_serializer_class()


class ExecutorPortfolioViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ExecutorPortfolioSerializer
    permission_classes = (permissions.ExecutorProfilePermission,)
    queryset = models.ExecutorPortfolioModel.objects.all()
    pagination_class = pagination.ExecutorPortfolioPagination

    def get_serializer_class(self):
        if self.action in ['create', 'partial_update', 'update']:
            return serializers.CreateExecutorPortfolioSerializer
        return super().get_serializer_class()


class ExecutorServiceViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ExecutorServiceSerializer
    permission_classes = (permissions.ExecutorProfilePermission,)
    queryset = models.ExecutorServicesModel.objects.all()
    pagination_class = pagination.ExecutorServicePagination

    def get_serializer_class(self):
        if self.action in ['create', 'partial_update', 'update']:
            return serializers.CreateExecutorServiceSerializer
        return super().get_serializer_class()


class ExecutorExperienceViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ExecutorExperienceSerializer
    permission_classes = (permissions.ExecutorProfilePermission,)
    queryset = models.ExecutorExperienceModel.objects.all()
    pagination_class = pagination.ExecutorExperiencePagination

    def get_serializer_class(self):
        if self.action in ['create', 'partial_update', 'update']:
            return serializers.CreateExecutorExperienceSerializer
        return super().get_serializer_class()


class ExecutorExperienceFileViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.CreateExecutorExperienceFileSerializer
    permission_classes = (permissions.ExecutorProfilePermission,)
    queryset = models.ExecutorExperienceFileModel.objects.all()


class ExecutorPortfolioAlbumViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ExecutorPortfolioAlbumSerializer
    permission_classes = (permissions.ExecutorPortfolioAlbumPermission,)
    queryset = models.ExecutorPortfolioAlbumModel.objects.all()
    
    def get_serializer_class(self):
        if self.action in ['create', 'partial_update', 'update']:
            return serializers.CreateExecutorPortfolioAlbumSerializer
        return super().get_serializer_class()
