from rest_framework import serializers
from . import models
from executor.serializers import ExecutorProfileSerializer
from client.serializers import ClientProfileSerializer
from category.serializers import SubCategorySerializer
from category.models import SubCategoryModel


class AllowedValuesSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AllowedValuesModel
        fields = ('id', 'name')


# class OrderSpecificSerializer(serializers.ModelSerializer):
#     allowed_values = AllowedValuesSerializer(many=True)
#     subcategory = serializers.SerializerMethodField()
#
#     class Meta:
#         model = models.OrderSpecificModel
#         exclude = ('subcategory_id', )
#
#     def get_subcategory(self, instance):
#         return SubCategorySerializer(
#             instance=SubCategoryModel.objects.filter(id=instance.get('subcategory_id')).first()
#         ).data


class CreateOrderSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = models.OrderModel
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    client = ClientProfileSerializer(read_only=True)
    executor = ExecutorProfileSerializer(read_only=True)
    # specifics = OrderSpecificSerializer(many=True, read_only=True)

    class Meta:
        model = models.OrderModel
        fields = '__all__'
