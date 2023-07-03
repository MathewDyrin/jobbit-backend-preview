from django.core.exceptions import ObjectDoesNotExist
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action

from . import models, serializers, services, permissions, pagination

from order.models import OrderModel
from executor.models import ExecutorProfileModel


class ChatViewSet(pagination.ChatsListPagination, viewsets.ModelViewSet):
    queryset = models.ChatModel.objects.all()
    serializer_class = serializers.ChatSerializer

    def list(self, request, *args, **kwargs):
        role = request.GET.get('role')
        user = request.user
        role_values = models.ParticipantModel.ParticipantRoles.values

        if not role:
            return Response({
                'detail': f'Arg `role` is required. Possible values: {role_values}'
            }, status=status.HTTP_400_BAD_REQUEST)

        if role not in role_values:
            return Response({
                'detail': f'Bad value for arg `role`. Possible values: {role_values}'
            }, status=status.HTTP_400_BAD_REQUEST)

        if not services.has_required_profile(user, role):
            return Response({
                'detail': 'User has not available profile for this role'
            }, status=status.HTTP_400_BAD_REQUEST)

        chats = models.ChatModel.objects.filter(
            participants__user=request.user).filter(participants__role=role).distinct()
        qs = self.paginate_queryset(chats, request, view=self)
        data = serializers.ChatSerializer(qs, many=True, context={'request': request}).data
        return self.get_paginated_response(data)

    def create(self, request, *args, **kwargs):
        serializer = serializers.CreateChatSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        response = dict()

        if not services.has_required_profile(user, serializer.validated_data['role']):
            return Response({
                'detail': 'User has not available profile for this role'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            order = OrderModel.objects.get(id=serializer.validated_data['order_id'])

            if serializer.validated_data['role'] == models.ParticipantModel.ParticipantRoles.CLIENT:
                services.is_order_author(user, order)

                try:
                    executor = ExecutorProfileModel.objects.get(id=serializer.validated_data['executor'])

                    p1 = services.create_participant(user, models.ParticipantModel.ParticipantRoles.CLIENT)
                    p2 = services.create_participant(executor.user, models.ParticipantModel.ParticipantRoles.EXECUTOR)

                    serializer.validated_data.pop('role')
                    serializer.validated_data.pop('order_id')
                    serializer.validated_data.pop('executor')

                    services.not_already_exist(p1, p2, order)
                    new_chat = serializer.create(serializer.validated_data)
                    new_chat.participants.add(p1, p2)
                    new_chat.associated_order = order
                    new_chat.save()
                    response.update(serializers.ChatSerializer(instance=new_chat, context={'request': request}).data)
                    return Response(response, status=status.HTTP_201_CREATED)
                except ObjectDoesNotExist:
                    return Response(status=status.HTTP_404_NOT_FOUND)

            if serializer.validated_data['role'] == models.ParticipantModel.ParticipantRoles.EXECUTOR:
                executor = ExecutorProfileModel.objects.get(user=user)
                if executor.balance < order.response_cost:
                    return Response({
                        'detail': 'You have insufficient balance for response'
                    }, status=status.HTTP_400_BAD_REQUEST)

                p1 = services.create_participant(order.client.user, models.ParticipantModel.ParticipantRoles.CLIENT)
                p2 = services.create_participant(user, models.ParticipantModel.ParticipantRoles.EXECUTOR)

                serializer.validated_data.pop('role')
                serializer.validated_data.pop('order_id')
                try:
                    serializer.validated_data.pop('executor')
                except KeyError:
                    pass

                services.not_already_exist(p1, p2, order)
                new_chat = serializer.create(serializer.validated_data)
                new_chat.participants.add(p1, p2)
                new_chat.associated_order = order
                new_chat.save()

                executor.balance -= order.response_cost
                executor.save()

                response.update(serializers.ChatSerializer(instance=new_chat, context={'request': request}).data)
                return Response(response, status=status.HTTP_201_CREATED)

        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @action(methods=['GET'], detail=False)
    def get_updates(self, request, *args, **kwargs):
        role = request.GET.get('role')
        user = request.user
        role_values = models.ParticipantModel.ParticipantRoles.values

        if not role:
            return Response({
                'detail': f'Arg `role` is required. Possible values: {role_values}'
            }, status=status.HTTP_400_BAD_REQUEST)

        if role not in role_values:
            return Response({
                'detail': f'Bad value for arg `role`. Possible values: {role_values}'
            }, status=status.HTTP_400_BAD_REQUEST)

        if not services.has_required_profile(user, role):
            return Response({
                'detail': 'User has not available profile for this role'
            }, status=status.HTTP_400_BAD_REQUEST)

        my_all_chats = models.ChatModel.objects.filter(
            participants__user__in=[user]
        ).filter(participants__role__in=[role])
        unread_messages = [chat.messages.filter(status=models.MessageModel.MessageStatus.NOT_READ)
                                        .exclude(author__user=request.user)
                                        .count()
                           for chat in my_all_chats]
        return Response({'count': sum(unread_messages)}, status=status.HTTP_200_OK)


class ParticipantViewSet(pagination.ChatParticipantsPagination, viewsets.ModelViewSet):
    permission_classes = (permissions.IsAdmin,)

    def list(self, request, *args, **kwargs):
        role = request.GET.get('role')
        user = request.user
        role_values = models.ParticipantModel.ParticipantRoles.values

        if not role:
            return Response({
                'detail': f'Arg `role` is required. Possible values: {role_values}'
            }, status=status.HTTP_400_BAD_REQUEST)

        if role not in role_values:
            return Response({
                'detail': f'Bad value for arg `role`. Possible values: {role_values}'
            }, status=status.HTTP_400_BAD_REQUEST)

        if not services.has_required_profile(user, role):
            return Response({
                'detail': 'User has not available profile for this role'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            chat = models.ChatModel.objects.get(id=kwargs['chat_id'])
            permissions.is_chat_participant(chat, request.user, role)
            qs = self.paginate_queryset(chat.participants.all(), request, view=self)
            data = serializers.ParticipantSerializer(qs, many=True).data
            return self.get_paginated_response(data)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def create(self, request, *args, **kwargs):
        try:
            chat = models.ChatModel.objects.get(id=kwargs['chat_id'])
            user = models.User.objects.get(username=request.data['username'])
            new_participant = services.create_participant(user)
            chat.participants.add(new_participant)
            data = serializers.ParticipantSerializer(new_participant).data
            return Response(data, status=status.HTTP_201_CREATED)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, *args, **kwargs):
        try:
            chat = models.ChatModel.objects.get(id=kwargs['chat_id'])
            chat.participants.remove(kwargs['pk'])
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class MessageViewSet(pagination.ChatHistoryPagination, viewsets.ModelViewSet):
    queryset = models.MessageModel.objects.all()
    serializer_class = serializers.MessageSerializer
    permission_classes = (permissions.IsMessageAuthor,)

    def list(self, request, *args, **kwargs):
        try:
            chat = models.ChatModel.objects.get(id=kwargs['chat_id'])
            permissions.is_chat_participant(chat, request.user)
            qs = self.paginate_queryset(chat.messages.all().order_by('-created_time'), request, view=self)
            not_my_messages = chat.messages.exclude(author__user=request.user)
            for obj in not_my_messages:
                obj.status = models.MessageModel.MessageStatus.READ
                obj.save()
            data = serializers.MessageSerializer(qs, many=True, context={'request': request}).data
            return self.get_paginated_response(data)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def create(self, request, *args, **kwargs):
        response = dict()
        role = request.GET.get('role')
        user = request.user
        role_values = models.ParticipantModel.ParticipantRoles.values

        if not role:
            return Response({
                'detail': f'Arg `role` is required. Possible values: {role_values}'
            }, status=status.HTTP_400_BAD_REQUEST)

        if role not in role_values:
            return Response({
                'detail': f'Bad value for arg `role`. Possible values: {role_values}'
            }, status=status.HTTP_400_BAD_REQUEST)

        if not services.has_required_profile(user, role):
            return Response({
                'detail': 'User has not available profile for this role'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            chat = models.ChatModel.objects.get(id=kwargs['chat_id'])
            permissions.is_chat_participant(chat, request.user, role)
            serializer = serializers.CreateMessageSerializer(data=request.data)
            if serializer.is_valid():
                new_message = serializer.create(serializer.validated_data)
                new_message.author = chat.participants.filter(user_id=request.user.id).filter(role=role).first()
                if request.data.get('files_url'):
                    services.add_files_to_obj(new_message, request.data['files_url'])
                new_message.save()
                chat.messages.add(new_message)
                response.update(serializers.MessageSerializer(instance=new_message).data)
                return Response(response, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def partial_update(self, request, *args, **kwargs):
        role = request.GET.get('role')
        user = request.user
        role_values = models.ParticipantModel.ParticipantRoles.values

        if not role:
            return Response({
                'detail': f'Arg `role` is required. Possible values: {role_values}'
            }, status=status.HTTP_400_BAD_REQUEST)

        if role not in role_values:
            return Response({
                'detail': f'Bad value for arg `role`. Possible values: {role_values}'
            }, status=status.HTTP_400_BAD_REQUEST)

        if not services.has_required_profile(user, role):
            return Response({
                'detail': 'User has not available profile for this role'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            chat = models.ChatModel.objects.get(id=kwargs['chat_id'])
            permissions.is_chat_participant(chat, request.user, role)
            message = chat.messages.get(pk=kwargs['pk'])
            serializer = self.get_serializer(message, data=request.data, partial=True)
            if request.data.get('files_url') is not None:
                if len(request.data['files_url']) == 0:
                    serializer.instance.files.all().delete()
                else:
                    serializer.instance.files.all().delete()
                    services.add_files_to_obj(serializer.instance, request.data['files_url'])
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
