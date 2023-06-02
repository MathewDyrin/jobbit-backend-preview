from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('profile', viewset=views.ClientProfileViewSet, basename='profile')

router2 = DefaultRouter()
router2.register('feedback', viewset=views.ClientFeedbackViewSet, basename='feedback')


urlpatterns = [
    path('verification/', views.CreateClientVerificationView.as_view()),
    path('', include(router.urls)),
    path('<str:client_id>/', include(router2.urls))
]
