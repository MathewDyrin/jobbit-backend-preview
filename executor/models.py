import datetime
import uuid

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth import get_user_model
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.translation import gettext_lazy as _
from category.models import SubCategoryModel
from executor.constants import DAYS_IN_18_YEARS
from geo.models import CityModel, SubwayModel

User = get_user_model()


class ExecutorProfileModel(models.Model):
    user = models.ForeignKey(
        to=User,
        related_name='executor_profiles',
        on_delete=models.CASCADE,
        unique=True
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(null=True, blank=True)
    username = models.CharField(max_length=28, null=True, blank=True)
    name = models.CharField(max_length=28, null=True, blank=True)
    last_name = models.CharField(max_length=28, null=True, blank=True)
    phone_number = PhoneNumberField(null=True, blank=True)
    bio = models.CharField(max_length=500, null=True, blank=True)
    birthdate = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)

    class Genders(models.TextChoices):
        MALE = 'M', _('Male')
        FEMALE = 'F', _('Female')
        OTHER = 'O', _('Other')
        NOT_STATED = 'N', _('Not stated')

    gender = models.CharField(max_length=1, null=True, blank=True, choices=Genders.choices)
    created_date = models.DateField(auto_now_add=True)
    avatar = models.URLField(null=True, blank=True)

    class Meta:
        db_table = 'executor_profile'
        verbose_name = 'Профиль исполнителя'
        verbose_name_plural = 'Профили исполнителей'

    def __str__(self):
        return str(self.email)


class ExecutorExperienceModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    start_date = models.DateField()
    finish_date = models.DateField()
    is_visible = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=False)
    executor_profile = models.ForeignKey(
        to=ExecutorProfileModel,
        related_name='executor_experiences',
        on_delete=models.CASCADE
    )

    class Meta:
        db_table = 'executor_experience'
        verbose_name = 'Опыт исполнителя'
        verbose_name_plural = 'Опыты исполнителей'

    def __str__(self):
        return str(self.name)


class ExecutorExperienceFileModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    photo = models.URLField()
    experience_entity = models.ForeignKey(
        to=ExecutorExperienceModel,
        related_name='experience_files',
        on_delete=models.CASCADE
    )

    class Meta:
        db_table = 'executor_experience_file'
        verbose_name = 'Файл опыта исполнителя'
        verbose_name_plural = 'Файлы опытов исполнителей'

    def __str__(self):
        return str(self.name)


class TimeUnit(models.TextChoices):
    MINUTELY = 'MINUTELY'
    MONTHLY = 'MONTHLY'
    WEEKLY = 'WEEKLY'
    HOURLY = 'HOURLY'
    DAILY = 'DAILY'
    HALF_DAY = 'HALF_DAY'
    H7 = '7H'
    H6 = '6H'
    H5 = '5H'
    M180 = '180M'
    M135 = '135M'
    M120 = '120M'
    M105 = '105M'
    M90 = '90M'
    M80 = '80M'
    M75 = '75M'
    M60 = '60M'
    M50 = '50M'
    M45 = '45M'
    M40 = '40M'
    M35 = '35M'
    M30 = '30M'
    M20 = '20M'
    M15 = '15M'


class ExecutorServicesModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    photo = models.URLField()
    category = models.ForeignKey(
        to=SubCategoryModel,
        related_name='executor_services',
        on_delete=models.CASCADE
    )
    description = models.CharField(max_length=100)
    price = models.FloatField()
    time_unit = models.CharField(max_length=20, choices=TimeUnit.choices)
    has_departure = models.BooleanField(default=False)
    departure_cost = models.FloatField()
    executor_profile = models.ForeignKey(
        to=ExecutorProfileModel,
        related_name='executor_services',
        on_delete=models.CASCADE
    )

    class Meta:
        db_table = 'executor_service'
        verbose_name = 'Услуга исполнителя'
        verbose_name_plural = 'Услуги исполнителя'


class ExecutorFeedbackModel(models.Model):
    from client.models import ClientProfileModel

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    text = models.CharField(max_length=500)
    answer = models.CharField(max_length=500)
    rate = models.IntegerField(validators=[MinValueValidator(1),
                                           MaxValueValidator(5)])
    author = models.ForeignKey(
        to=ClientProfileModel,
        related_name='executor_feedbacks',
        on_delete=models.CASCADE
    )
    executor_profile = models.ForeignKey(
        to=ExecutorProfileModel,
        related_name='executor_feedbacks',
        on_delete=models.CASCADE
    )

    class Meta:
        db_table = 'executor_feedback'
        verbose_name = 'Отзыв о исполнителе'
        verbose_name_plural = 'Отзывы о исполнителях'

    def __str__(self):
        return f'{self.text[:30]} {self.rate}'


class ExecutorPortfolioModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    description = models.CharField(max_length=500)
    photo = models.URLField()
    categories = models.ManyToManyField(
        to=SubCategoryModel,
        related_name='executors_portfolio',
        null=True,
        blank=True
    )
    executor_profile = models.ForeignKey(
        to=ExecutorProfileModel,
        related_name='executor_portfolios',
        on_delete=models.CASCADE
    )

    class Meta:
        db_table = 'executor_portfolio'
        verbose_name = 'Портфолио исполнителя'
        verbose_name_plural = 'Портфолио исполнителей'

    def __str__(self):
        return f'{self.description[:30]}'


class ExecutorAddressModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    street = models.CharField(max_length=100)
    home = models.CharField(max_length=25)
    office = models.CharField(max_length=25)
    room = models.CharField(max_length=25)
    index = models.CharField(max_length=50)
    city = models.ForeignKey(
        to=CityModel,
        related_name='executor_addresses',
        on_delete=models.CASCADE
    )
    executor_profile = models.ForeignKey(
        to=ExecutorProfileModel,
        related_name='executor_addresses',
        on_delete=models.CASCADE,
        unique=True
    )


class ExecutorGeoModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    remote_work_ability = models.BooleanField(default=True)
    subways = models.ManyToManyField(
        to=SubwayModel,
        related_name='executor_geos',
        null=True,
        blank=True
    )
    executor_profile = models.ForeignKey(
        to=ExecutorProfileModel,
        related_name='executor_geos',
        on_delete=models.CASCADE
    )

    class Meta:
        db_table = 'executor_geo'
        verbose_name = 'Геоданные исполнителя'
        verbose_name_plural = 'Геоданные исполнителей'


class ExecutorVerificationModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField('Имя', max_length=255)
    middle_name = models.CharField('Отчество', max_length=255, null=True, blank=True)
    last_name = models.CharField('Фамилия', max_length=255)
    birthday = models.DateField('Дата рождения')
    address = models.CharField('Адрес проживания', max_length=255)
    passport_photo_url = models.URLField('Фото паспорта')
    selfie_with_passport_url = models.URLField('Фото с паспортом')
    executor = models.ForeignKey(
        verbose_name='Исполнитель',
        to=ExecutorProfileModel,
        related_name='executor_verifications',
        on_delete=models.CASCADE,
        unique=True
    )

    class Meta:
        db_table = 'executor_verification'
        verbose_name = 'Верификация Исполнителя'
        verbose_name_plural = 'Верификации Исполнителей'

    def get_full_name(self) -> str:
        return f'{self.last_name} {self.first_name} {self.middle_name}'

    def __str__(self) -> str:
        return f'{self.get_full_name()}'

    def save(self, *args, **kwargs):
        today = datetime.date.today()
        if today - datetime.timedelta(days=DAYS_IN_18_YEARS) > self.birthday:
            super().save(*args, **kwargs)
        else:
            raise Exception('Возраст должен быть больше 18')
