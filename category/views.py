from rest_framework.generics import ListAPIView

from . import serializers, models


class CategoryListView(ListAPIView):
    serializer_class = serializers.CategorySerializer
    queryset = models.CategoryModel.objects.all()


class SubCategoryListView(ListAPIView):
    serializer_class = serializers.SubCategorySerializer
    queryset = models.SubCategoryModel.objects.all()
