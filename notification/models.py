import uuid
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from user.models import User


class NotificationStatus(models.TextChoices):
    READ = 'Прочитано', _('READ')
    UNREAD = 'Не прочитано', _('UNREAD')


class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=True)
    icon = models.URLField(
        'Иконка',
        null=True,
        blank=True,
        default='https://png.pngtree.com/png-vector/20190505/ourmid/pngtree-vector-notification-icon-png-image_1022639.jpg'
    )
    status = models.CharField(
        'Статус',
        max_length=12,
        null=True,
        blank=True,
        choices=NotificationStatus.choices,
        default=NotificationStatus.UNREAD
    )
    title = models.CharField('Заголовок', max_length=500, blank=False, null=False)
    content = models.TextField('Контент', null=True, blank=True)
    date = models.DateTimeField('Дата', null=False, default=timezone.now)
    user = models.ForeignKey(verbose_name='Пользователь', to=User, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f'{self.user}: {self.title}'
