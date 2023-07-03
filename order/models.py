import uuid
# from djongo import models
from django.db import models
from django.contrib.postgres.fields import ArrayField

from client.models import ClientProfileModel
from executor.models import ExecutorProfileModel
from geo.models import CityModel, CountryModel, SubwayModel
from category.models import SubCategoryModel


def gen_order_num():
    largest = OrderModel.objects.order_by('-number').first()
    if not largest:
        return 10000
    return largest.number + 1


class AllowedValuesModel(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    name = models.CharField(max_length=255)


# class OrderSpecificModel(models.Model):
#     id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
#     title = models.CharField(max_length=255)
#     subcategory_id = models.CharField(max_length=512, null=True, blank=True)
#     allowed_values = models.ArrayField(model_container=AllowedValuesModel, default=[])
#
#     def __str__(self):
#         return f'{self.title}'


class StatusChoices(models.TextChoices):
    ON_MODERATION = 'ON_MODERATION', 'На модерации'
    DENIED = 'DENIED', 'Отклонен'
    ACTIVE = 'ACTIVE', 'Активен'
    WAITING = 'WAITING', 'Ожидает пополнения'
    CANCELED = 'CANCELED', 'Отменен'
    EXECUTING = 'EXECUTING', 'Выполняется'
    COMPLETED = 'COMPLETED', 'Завершен'
    APPEAL = 'APPEAL', 'Апелляция'
    
    
class OrderModelGeoMixin(models.Model):
    country = models.ForeignKey(CountryModel, related_name='orders', null=True, on_delete=models.SET_NULL)
    city = models.ForeignKey(CityModel, related_name='orders', null=True, on_delete=models.SET_NULL)
    street = models.CharField('Улица', max_length=255, null=True, blank=True)
    house = models.CharField('Дом', max_length=255, null=True, blank=True)
    office = models.CharField('Офис', max_length=255, null=True, blank=True)
    longitude = models.FloatField('Долгота', default=0, null=True, blank=True)
    latitude = models.FloatField('Широта', default=0, null=True, blank=True)
    subway = models.ForeignKey(SubwayModel, related_name='orders', null=True, on_delete=models.SET_NULL)
    
    class Meta:
        db_table = 'order_geo'


class OrderModel(models.Model):
    number = models.BigIntegerField('Номер заказа', default=gen_order_num)
    title = models.CharField('Заголовок', max_length=512)
    description = models.TextField('Описание')
    created_at = models.DateTimeField('Время создания', auto_now_add=True)
    updated_at = models.DateTimeField('Время последнего обновления', auto_now=True)
    budget = models.FloatField('Бюджет', null=True, blank=True)
    start_date = models.DateField('Дата когда нужно приступить', null=True, blank=True)
    end_date = models.DateField('Дата когда нужно закончить', null=True, blank=True)
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
    # specifics = models.ArrayField(model_container=OrderSpecificModel)
    # objects = models.DjongoManager()

    # Response cost
    response_cost = models.FloatField(default=1)

    class Meta:
        db_table = 'order'
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f'{self.title}'
