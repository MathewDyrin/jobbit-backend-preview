from django.urls import path

from . import views

urlpatterns = [
    path('city/', views.CityListView.as_view()),
    path('country/', views.CountryListView.as_view()),
    path('region/', views.RegionListView.as_view()),
    path('subway_branch/', views.SubwayBranchListView.as_view()),
    path('subway/', views.SubwayListView.as_view()),
]
