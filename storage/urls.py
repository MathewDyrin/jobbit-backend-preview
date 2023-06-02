from django.urls import path
from . import views

urlpatterns = [
    path('', views.Storage.as_view()),
]
