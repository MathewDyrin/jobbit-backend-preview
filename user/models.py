import uuid
import datetime
from django.utils import timezone
from django.db import models
from django.contrib.auth import models as auth_models
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver

from .constants import DAYS_IN_18_YEARS


class Genders(models.TextChoices):
    MALE = 'M', _('Male')
    FEMALE = 'F', _('Female')
    OTHER = 'O', _('Other')
    NOT_STATED = 'N', _('Not stated')


class Guest(auth_models.AnonymousUser):
    # custom fields

    def save(self):
        pass

    def delete(self):
        pass

    def set_password(self, raw_password):
        pass

    def check_password(self, raw_password):
        pass


class UserSettingsMixin(models.Model):
    # 2FA settings
    class Type2FA(models.TextChoices):
        EMAIL = 'EMAIL', _('EMAIL')
        PHONE = 'PHONE', _('PHONE')

    is_2FA_enabled = models.BooleanField(default=False)
    type_2FA = models.CharField(
        max_length=6, null=False, blank=True, choices=Type2FA.choices, default=Type2FA.EMAIL
    )

    class Meta:
        abstract = True


class UserManager(auth_models.BaseUserManager):
    def create_user(self, email, password):
        if not email:
            raise ValueError('Email address is not provided')
        if not password:
            raise ValueError('Password is not provided')
        user = self.model(
            email=self.normalize_email(email)
        )
        user.set_password(password)
        user.save()
        return user

    def create_staff_member(self, email, password):
        user = self.create_user(email, password)
        user.is_staff_member = True
        user.save()
        return user

    def create_superuser(self, email, password):
        user = self.create_user(email, password)
        user.is_superuser = True
        user.save()
        return user

    def get_by_natural_key(self, username):
        if isinstance(username, dict):
            return self.get(**{username['key']: username['value']})
        else:
            return super().get_by_natural_key(username)


# Permission mixin provides is_superuser field and checks perms for login admin site
class User(UserSettingsMixin, auth_models.PermissionsMixin, auth_models.AbstractBaseUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(null=True, blank=True, unique=True)
    phone_number = PhoneNumberField(null=True, blank=True, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff_member = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'

    objects = UserManager()

    # for accessing admin page
    @property
    def is_staff(self):
        return self.is_superuser

    def __str__(self):
        return str(self.email)


class Session(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    key = models.CharField(max_length=64, null=False)
    # Time info
    created_date = models.DateTimeField(null=False, default=timezone.now)
    last_updated_date = models.DateTimeField(null=False, default=timezone.now)
    ip = models.CharField(max_length=15, null=True)
    # Device info
    device_family = models.CharField(max_length=25, null=True)
    device_brand = models.CharField(max_length=25, null=True)
    device_model = models.CharField(max_length=25, null=True)
    # Os info
    os_family = models.CharField(max_length=25, null=True)
    os_version_string = models.CharField(max_length=25, null=True)
    # Browser info
    browser_family = models.CharField(max_length=25, null=True)
    browser_version_string = models.CharField(max_length=25, null=True)
    # JWT refresh
    refresh_token = models.CharField(max_length=500, null=True)

    def __str__(self):
        return f"Session_{self.user} object ({self.pk})"


# Administrator model
class StaffMember(models.Model):
    # staff member fields
    user = models.ForeignKey(User, unique=True, on_delete=models.CASCADE)


class Admin(models.Model):
    # admin fields
    user = models.ForeignKey(User, unique=True, on_delete=models.CASCADE)


# move to signals.py later
# this signals is used for automatically create or delete admin and staff instances
# if user instance was created or deleted

@receiver(post_save, sender=User, dispatch_uid='create_staff_member')
def create_staff_member(sender, instance, **kwargs):
    if instance.is_staff_member and not StaffMember.objects.filter(user=instance).count():
        StaffMember.objects.create(user=instance)


@receiver(post_save, sender=User, dispatch_uid='delete_staff_member')
def delete_staff_member(sender, instance, **kwargs):
    if not instance.is_staff_member:
        try:
            instance.staffmember_set.get().delete()
        except StaffMember.DoesNotExist:
            pass


@receiver(post_save, sender=User, dispatch_uid='create_admin')
def create_admin(sender, instance, **kwargs):
    if instance.is_superuser and not Admin.objects.filter(user=instance).count():
        Admin.objects.create(user=instance)


@receiver(post_save, sender=User, dispatch_uid='delete_admin')
def delete_admin(sender, instance, **kwargs):
    if not instance.is_superuser:
        try:
            instance.admin_set.get().delete()
        except Admin.DoesNotExist:
            pass


# TODO: Use as basement to implement client profile and executor profile verification
# class Verification(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     first_name = models.CharField('Имя', max_length=255)
#     middle_name = models.CharField('Отчество', max_length=255)
#     last_name = models.CharField('Фамилия', max_length=255)
#     birthday = models.DateField('Дата рождения')
#     address = models.CharField('Адресс проживания', max_length=255)
#     passport_photo_url = models.URLField('Фото паспорта')
#     selfie_with_passport_url = models.URLField('Фото с паспортом')
#     user = models.ForeignKey(
#         verbose_name='Пользователь',
#         to=User,
#         related_name='verifications',
#         on_delete=models.CASCADE,
#         unique=True
#     )
#
#     class Meta:
#         verbose_name = 'Верификация'
#         verbose_name_plural = 'Верификации'
#
#     def get_full_name(self) -> str:
#         return f'{self.last_name} {self.first_name} {self.middle_name}'
#
#     def __str__(self) -> str:
#         return f'{self.get_full_name()}'
#
#     def save(self, *args, **kwargs):
#         today = datetime.date.today()
#         if today - datetime.timedelta(days=DAYS_IN_18_YEARS) > self.birthday:
#             super().save(*args, **kwargs)
#         else:
#             raise Exception('Возраст должен быть больше 18')
