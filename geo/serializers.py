from rest_framework import serializers

from . import models


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CountryModel
        fields = '__all__'


class RegionSerializer(serializers.ModelSerializer):
    country = CountrySerializer(read_only=True)

    class Meta:
        model = models.RegionModel
        fields = '__all__'


class CitySerializer(serializers.ModelSerializer):
    region = RegionSerializer(read_only=True)

    class Meta:
        model = models.CityModel
        fields = '__all__'


class SubwayBranchSerializer(serializers.ModelSerializer):
    city = CitySerializer(read_only=True)

    class Meta:
        model = models.SubwayBranchModel
        fields = '__all__'


class SubwaySerializer(serializers.ModelSerializer):
    branch = SubwayBranchSerializer(read_only=True)

    class Meta:
        model = models.SubwayModel
        fields = '__all__'
