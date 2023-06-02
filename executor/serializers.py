from rest_framework import serializers

from . import models
from user.serializers import UserSerializer
from geo.serializers import CitySerializer, SubwaySerializer
from category.serializers import SubCategorySerializer


class CreateExecutorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ExecutorProfileModel
        fields = '__all__'
        read_only_fields = ('is_verified', 'created_date')


class ExecutorProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = models.ExecutorProfileModel
        fields = '__all__'
        read_only_fields = ('is_verified', 'created_date')


class CreateExecutorVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ExecutorVerificationModel
        fields = '__all__'


class ExecutorVerificationSerializer(serializers.ModelSerializer):
    executor = ExecutorProfileSerializer(read_only=True)

    class Meta:
        model = models.ExecutorVerificationModel
        fields = '__all__'


class CreateExecutorFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ExecutorFeedbackModel
        fields = '__all__'
        read_only_fields = ('answer',)


class ExecutorFeedbackSerializer(serializers.ModelSerializer):
    client_profile = ExecutorProfileSerializer(read_only=True)

    class Meta:
        model = models.ExecutorFeedbackModel
        fields = '__all__'
        read_only_fields = ('answer',)


class AnswerOnFeedbackSerializer(serializers.ModelSerializer):
    executor_profile = ExecutorProfileSerializer(read_only=True)

    class Meta:
        model = models.ExecutorFeedbackModel
        fields = '__all__'


class CreateExecutorAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ExecutorAddressModel
        fields = '__all__'


class ExecutorAddressSerializer(serializers.ModelSerializer):
    city = CitySerializer(read_only=True)
    executor_profile = ExecutorProfileSerializer(read_only=True)

    class Meta:
        model = models.ExecutorAddressModel
        fields = '__all__'


class CreateExecutorGeoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ExecutorGeoModel
        fields = '__all__'


class ExecutorGeoSerializer(serializers.ModelSerializer):
    executor_profile = ExecutorProfileSerializer(read_only=True)
    subways = SubwaySerializer(read_only=True, many=True)

    class Meta:
        model = models.ExecutorGeoModel
        fields = '__all__'


class CreateExecutorPortfolioSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ExecutorPortfolioModel
        fields = '__all__'


class ExecutorPortfolioSerializer(serializers.ModelSerializer):
    executor_profile = ExecutorProfileSerializer(read_only=True)
    categories = SubCategorySerializer(read_only=True, many=True)

    class Meta:
        model = models.ExecutorPortfolioModel
        fields = '__all__'


class CreateExecutorSerivceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ExecutorServicesModel
        fields = '__all__'


class ExecutorServiceSerializer(serializers.ModelSerializer):
    executor_profile = ExecutorProfileSerializer(read_only=True)
    category = SubCategorySerializer(read_only=True)

    class Meta:
        model = models.ExecutorServicesModel
        fields = '__all__'


class CreateExecutorExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ExecutorExperienceModel
        fields = '__all__'


class CreateExecutorExperienceFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ExecutorExperienceFileModel
        fields = '__all__'


class ExecutorExperienceSerializer(serializers.ModelSerializer):
    executor_profile = ExecutorProfileSerializer(read_only=True)
    files = serializers.SerializerMethodField()

    class Meta:
        model = models.ExecutorExperienceModel
        fields = '__all__'

    def get_files(self, instance):
        return CreateExecutorExperienceFileSerializer(
            instance.experience_files.all(),
            many=True
        ).data
