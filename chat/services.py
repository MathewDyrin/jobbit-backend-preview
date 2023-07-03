from . import serializers, models
from order.models import OrderModel
from user.models import User
from client.models import ClientProfileModel
from executor.models import ExecutorProfileModel
from rest_framework.exceptions import PermissionDenied
from django.core.exceptions import ObjectDoesNotExist


def create_participant(user: User = None, role=None):
    filters = {'user': str(user.id)}
    search_filters = {'user_id': str(user.id), 'role': None}
    if role:
        filters['role'] = role
        search_filters['role'] = role
    if models.ParticipantModel.objects.filter(**search_filters).exists():
        return models.ParticipantModel.objects.filter(**search_filters).first()
    else:
        serializer = serializers.CreateParticipantSerializer(data=filters)
        if serializer.is_valid():
            return serializer.create(serializer.validated_data)
        else:
            raise Exception(serializer.errors)


def add_files_to_obj(obj, file_urls):
    for url in file_urls:
        try:
            file = models.ChatFileModel.objects.get(file_url=url)
            obj.files.add(file)
        except ObjectDoesNotExist:
            new_file = models.ChatFileModel.objects.create(file_url=url)
            obj.files.add(new_file)
    obj.save()


def not_already_exist(p1: models.ParticipantModel, p2: models.ParticipantModel, order: OrderModel):
    if models.ChatModel.objects.filter(
            participants=p1).filter(participants=p2).filter(associated_order=order).exists():
        raise PermissionDenied


def has_required_profile(user: User, role: models.ParticipantModel.ParticipantRoles) -> bool:
    if role == models.ParticipantModel.ParticipantRoles.CLIENT:
        return ClientProfileModel.objects.filter(user=user).exists()
    if role == models.ParticipantModel.ParticipantRoles.EXECUTOR:
        return ExecutorProfileModel.objects.filter(user=user).exists()
    return False


def is_order_author(user: User, order: OrderModel):
    if order.client != ClientProfileModel.objects.get(user=user):
        raise PermissionDenied
