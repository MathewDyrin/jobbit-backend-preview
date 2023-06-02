import uuid

from django.db import models


class CategoryModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=28)
    description = models.CharField(max_length=500)
    is_visible = models.BooleanField(default=True)

    class Meta:
        db_table = 'category'
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class SubCategoryModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=28)
    description = models.CharField(max_length=500)
    is_visible = models.BooleanField(default=True)
    category = models.ForeignKey(
        to=CategoryModel,
        related_name='subcategories',
        on_delete=models.CASCADE
    )

    class Meta:
        db_table = 'subcategory'
        verbose_name = 'Подкатегория'
        verbose_name_plural = 'Подкатегории'
