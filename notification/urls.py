from django.urls import path
from django.urls import include
from rest_framework.routers import DefaultRouter

from .views import NotificationView

router = DefaultRouter()

router.register('notification', NotificationView, basename='notification')

urlpatterns = [
    path('api/v1/', include(router.urls)),
]
