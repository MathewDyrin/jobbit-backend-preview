from django.urls import path

from . import views


urlpatterns = [
    path('category/', views.CategoryListView.as_view()),
    path('sub_category/', views.SubCategoryListView.as_view()),
]
