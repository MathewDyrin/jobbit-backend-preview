import uuid

from django.db import models
from django.contrib.auth import get_user_model

from order.models import OrderModel

User = get_user_model()


class ChatFileModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file_url = models.URLField('Ссылка на файл', unique=True)

    class Meta:
        db_table = 'order_file'
        verbose_name = 'Файл чата'
        verbose_name_plural = 'Файлы чата'

    def __str__(self):
        return f'{self.file_url}'


class ParticipantModel(models.Model):
    class ParticipantRoles(models.TextChoices):
        CLIENT = 'CLIENT'
        EXECUTOR = 'EXECUTOR'
        MODERATOR = 'MODERATOR'

    user = models.ForeignKey(
        verbose_name='Участник',
        to=User,
        related_name='participants',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    role = models.CharField(
        'Роль',
        max_length=99,
        choices=ParticipantRoles.choices
    )

    class Meta:
        db_table = 'chat_participant'
        verbose_name = 'Участник чата'
        verbose_name_plural = 'Участники чатов'

    def __str__(self):
        return f'{self.user} - {self.role}'


class MessageModel(models.Model):
    class MessageStatus(models.TextChoices):
        READ = 'Прочитано',
        NOT_READ = 'Не прочитано'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(
        verbose_name='Участник',
        to=ParticipantModel,
        related_name='messages',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    text = models.TextField('Текст сообщения', null=True, blank=True)
    audio = models.URLField('Аудиосообщение', null=True, blank=True)
    files = models.ManyToManyField(
        verbose_name='Файлы для сообщения',
        to=ChatFileModel,
        related_name='messages',
        null=True,
        blank=True
    )
    created_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        'Статус',
        max_length=99,
        choices=MessageStatus.choices,
        default=MessageStatus.NOT_READ
    )
    answer = models.ForeignKey(
        verbose_name='Ответ',
        to='MessageModel',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    class Meta:
        db_table = 'chat_message'
        verbose_name = 'Сообщение чата'
        verbose_name_plural = 'Сообщения чатов'


class ChatModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField('Название', max_length=512)
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)
    cover = models.URLField('Заставка')
    messages = models.ManyToManyField(
        verbose_name='Сообщения',
        to=MessageModel,
        related_name='chats',
        null=True,
        blank=True
    )
    participants = models.ManyToManyField(
        verbose_name='Участники',
        to=ParticipantModel,
        related_name='chats',
        null=True,
        blank=True
    )
    associated_order = models.ForeignKey(
        verbose_name='Связанный заказ',
        to=OrderModel,
        related_name='chats',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    class Meta:
        db_table = 'chat'
        verbose_name = 'Чат'
        verbose_name_plural = 'Чаты'

    def __str__(self):
        return f'{self.title}'


class ChatPermissionsModel(models.Model):
    allow_update = models.BooleanField('Разрешить обновление', default=False)
    allow_delete = models.BooleanField('Разрешить удаление', default=False)
    allow_add_participant = models.BooleanField('Разрешить добавлять участников', default=False)
    allow_remove_participant = models.BooleanField('Разрешить удалять участников', default=False)
    user = models.ForeignKey(
        verbose_name='Участник',
        to=User,
        related_name='chat_permissions',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    class Meta:
        db_table = 'chat_permission'
        verbose_name = 'Разрешение для чата'
        verbose_name_plural = 'Разрешения для чатов'
