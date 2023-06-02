import uuid

from django.db import models
from django.core.validators import RegexValidator


class CountryModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)

    class Meta:
        db_table = 'country'
        verbose_name = 'Страна'
        verbose_name_plural = 'Страны'

    def __str__(self):
        return self.name


class RegionModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    country = models.ForeignKey(
        to=CountryModel,
        related_name='regions',
        on_delete=models.CASCADE
    )

    class Meta:
        db_table = 'region'
        verbose_name = 'Регион'
        verbose_name_plural = 'Регионы'

    def __str__(self):
        return self.name


class CityModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    longitude = models.FloatField(default=0.00)
    latitude = models.FloatField(default=0.00)
    region = models.ForeignKey(
        to=RegionModel,
        related_name='cities',
        on_delete=models.CASCADE
    )

    class Meta:
        db_table = 'city'
        verbose_name = 'Город'
        verbose_name_plural = 'Города'

    def __str__(self):
        return self.name


class SubwayBranchModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    color = models.CharField(
        max_length=10,
        validators=[RegexValidator(regex=r'^#(?:[0-9a-fA-F]{3}){1,2}$',
                                   message='HEX isn\'t valid')]
    )
    city = models.ForeignKey(
        to=CityModel,
        related_name='subway_branches',
        on_delete=models.CASCADE
    )

    class Meta:
        db_table = 'subway_branch'
        verbose_name = 'Ветка метро'
        verbose_name_plural = 'Ветки метро'

    def __str__(self):
        return self.name


class SubwayModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    longitude = models.FloatField(default=0.00)
    latitude = models.FloatField(default=0.00)
    city = models.ForeignKey(
        to=CityModel,
        related_name='subways',
        on_delete=models.CASCADE
    )
    branch = models.ForeignKey(
        to=SubwayBranchModel,
        related_name='subway_branches',
        on_delete=models.CASCADE
    )

    class Meta:
        db_table = 'subway'
        verbose_name = 'Метро'
        verbose_name_plural = 'Метро'

    def __str__(self):
        return self.name
