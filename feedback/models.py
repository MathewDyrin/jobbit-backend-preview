from django.db import models
from django.contrib.auth import get_user_model

from factory.models import FactoryModel
from order.models import FileModel

User = get_user_model()


class AnswerModel(models.Model):
    text = models.TextField('Содержание ответа')
    author = models.ForeignKey(
        verbose_name='Автор',
        to=User,
        related_name='answers',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    files = models.ManyToManyField(
        verbose_name='Файлы ответа',
        to=FileModel,
        related_name='answers',
        null=True,
        blank=True
    )

    class Meta:
        db_table = 'feedback_answer'
        verbose_name = 'Ответ'
        verbose_name_plural = 'Ответы'


class FeedbackModel(models.Model):
    text = models.TextField('Содержание отзыва')
    files = models.ManyToManyField(
        verbose_name='Файлы отзыва',
        to=FileModel,
        related_name='feedbacks',
        null=True,
        blank=True
    )
    author_user = models.ForeignKey(
        to=User,
        on_delete=models.SET_NULL,
        related_name='feedback_user',
        null=True,
        blank=True
    )
    author_factory = models.ForeignKey(
        to=FactoryModel,
        on_delete=models.SET_NULL,
        related_name='feedback_author',
        null=True,
        blank=True
    )
    answers = models.ManyToManyField(
        verbose_name='Ответы',
        to=AnswerModel,
        related_name='feedbacks',
        null=True,
        blank=True
    )
    on_user = models.ForeignKey(
        to=User,
        on_delete=models.SET_NULL,
        related_name='my_feedback',
        null=True,
        blank=True
    )
    on_factory = models.ForeignKey(
        to=FactoryModel,
        on_delete=models.SET_NULL,
        related_name='my_feedback',
        null=True,
        blank=True
    )

    class Meta:
        db_table = 'feedback'
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'

    def __str__(self):
        return f'{self.text}'[:30]
