from rest_framework.generics import ListAPIView

from . import models, serializers


class CountryListView(ListAPIView):
    queryset = models.CountryModel.objects.all()
    serializer_class = serializers.CountrySerializer


class RegionListView(ListAPIView):
    queryset = models.RegionModel.objects.all()
    serializer_class = serializers.RegionSerializer


class CityListView(ListAPIView):
    queryset = models.CityModel.objects.all()
    serializer_class = serializers.CitySerializer


class SubwayBranchListView(ListAPIView):
    queryset = models.SubwayBranchModel.objects.all()
    serializer_class = serializers.SubwayBranchSerializer


class SubwayListView(ListAPIView):
    queryset = models.SubwayModel.objects.all()
    serializer_class = serializers.SubwaySerializer
