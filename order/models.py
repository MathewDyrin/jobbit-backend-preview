import typing
import uuid

from client.models import ClientProfileModel
from executor.models import ExecutorProfileModel
from djongo import models


def gen_order_num():
    largest = OrderModel.objects.order_by('-number').first()
    if not largest:
        return 10000
    return largest.number + 1


class OrderSpecificModel(models.Model):
    _id = models.ObjectIdField()
    title = models.CharField(max_length=255)
    text = models.TextField()

    class Meta:
        db_table = 'order_specific'
        managed = False

    def __str__(self):
        return f'{self.title}'


class StatusChoices(models.TextChoices):
    ON_MODERATION = 'ON_MODERATION', 'На модерации'
    DENIED = 'DENIED', 'Отклонен'
    ACTIVE = 'ACTIVE', 'Активен'
    WAITING = 'WAITING', 'Ожидает пополнения'
    CANCELED = 'CANCELED', 'Отменен'
    EXECUTING = 'EXECUTING', 'Выполняется'
    COMPLETED = 'COMPLETED', 'Завершен'
    APPEAL = 'APPEAL', 'Апелляция'


class OrderModel(models.Model):
    number = models.BigIntegerField('Номер заказа', default=gen_order_num)
    title = models.CharField('Заголовок', max_length=512)
    description = models.TextField('Описание')
    created_at = models.DateTimeField('Время создания', auto_now_add=True)
    updated_at = models.DateTimeField('Время последнего обновления', auto_now=True)
    longitude = models.FloatField('Долгота', default=0)
    latitude = models.FloatField('Широта', default=0)
    budget = models.FloatField('Бюджет', null=True, blank=True)
    start_date = models.DateField('Дата когда нужно приступить', null=True, blank=True)
    end_date = models.DateField('Дата когда нужно закончить', null=True, blank=True)
    comment = models.TextField('Комментарий к заказу', null=True, blank=True, default='')
    status = models.CharField(
        max_length=99,
        choices=StatusChoices.choices,
        default=StatusChoices.ON_MODERATION
    )
    client = models.ForeignKey(
        verbose_name='Заказчик',
        to=ClientProfileModel,
        related_name='orders',
        on_delete=models.CASCADE,
        null=True
    )
    executor = models.ForeignKey(
        verbose_name='Исполнитель',
        to=ExecutorProfileModel,
        related_name='orders',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    specifics = models.ArrayField(model_container=OrderSpecificModel)
    objects = models.DjongoManager()

    class Meta:
        db_table = 'order'
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f'{self.title}'
