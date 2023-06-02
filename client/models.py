import datetime
import uuid

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth import get_user_model
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.translation import gettext_lazy as _
from client.constants import DAYS_IN_18_YEARS

User = get_user_model()


class ClientProfileModel(models.Model):
    user = models.ForeignKey(
        to=User,
        related_name='client_profiles',
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
        db_table = 'client_profile'
        verbose_name = 'Профиль клиента'
        verbose_name_plural = 'Профили клиентов'

    def __str__(self):
        return str(self.email)


class ClientFeedbackModel(models.Model):
    from executor.models import ExecutorProfileModel

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    text = models.CharField(max_length=500)
    answer = models.CharField(max_length=500)
    rate = models.IntegerField(validators=[MinValueValidator(1),
                                           MaxValueValidator(5)])
    author = models.ForeignKey(
        to=ExecutorProfileModel,
        related_name='client_feedbacks',
        on_delete=models.CASCADE
    )
    client_profile = models.ForeignKey(
        to=ClientProfileModel,
        related_name='client_feedbacks',
        on_delete=models.CASCADE
    )

    class Meta:
        db_table = 'client_feedback'
        verbose_name = 'Отзыв о клиенте'
        verbose_name_plural = 'Отзывы о клиентах'

    def __str__(self):
        return f'{self.text[:30]} {self.rate}'


class ClientVerificationModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField('Имя', max_length=255)
    middle_name = models.CharField('Отчество', max_length=255, null=True, blank=True)
    last_name = models.CharField('Фамилия', max_length=255)
    birthday = models.DateField('Дата рождения')
    address = models.CharField('Адресс проживания', max_length=255)
    passport_photo_url = models.URLField('Фото паспорта')
    selfie_with_passport_url = models.URLField('Фото с паспортом')
    client = models.ForeignKey(
        verbose_name='Клиент',
        to=ClientProfileModel,
        related_name='client_verifications',
        on_delete=models.CASCADE,
        unique=True
    )

    class Meta:
        db_table = 'client_verification'
        verbose_name = 'Верификация Клиента'
        verbose_name_plural = 'Верификации Клиентов'

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
