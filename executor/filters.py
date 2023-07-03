from django_filters import rest_framework

from .models import ExecutorProfileModel


class CharFilterInFilter(rest_framework.BaseInFilter, rest_framework.CharFilter):
    pass


class ExecutorFilters(rest_framework.FilterSet):
    price = rest_framework.RangeFilter(field_name='executor_services__price')
    subcategory = CharFilterInFilter(field_name='executor_services__category__name', 
                                     lookup_expr='in')
    category = CharFilterInFilter(field_name='executor_services__category__category__name', 
                                  lookup_expr='in')
    rate = rest_framework.RangeFilter(field_name='executor_feedbacks__rate')
    city = CharFilterInFilter(field_name='executor_addresses__city__name', lookup_expr='in')
    region = CharFilterInFilter(field_name='executor_addresses__city__region__name', 
                                lookup_expr='in')
    country = CharFilterInFilter(field_name='executor_addresses__city__region__country__name', 
                                 lookup_expr='in')
    subways = CharFilterInFilter(field_name='executor_geos__subways__name', 
                                 lookup_expr='in')
    
    
    class Meta:
        model = ExecutorProfileModel
        fields = ('price', 'category', 'subcategory', 'rate', 'city', 'region', 'country')
    
    