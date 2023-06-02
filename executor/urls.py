from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('profile', viewset=views.ExecutorProfileViewSet, basename='profile')
router.register('address', viewset=views.ExecutorAddressViewSet, basename='address')
router.register('geo', viewset=views.ExecutorGeoViewSet, basename='geo')
router.register('portfolio', viewset=views.ExecutorGeoViewSet, basename='portfolio')
router.register('service', viewset=views.ExecutorServiceViewSet, basename='service')
router.register('experience', viewset=views.ExecutorExperienceViewSet, basename='experience')
router.register('experience_file', viewset=views.ExecutorExperienceFileViewSet, basename='experience_file')

router2 = DefaultRouter()
router2.register('feedback', viewset=views.ExecutorFeedbackViewSet, basename='feedback')


urlpatterns = [
    path('verification/', views.CreateExecutorVerificationView.as_view()),
    path('', include(router.urls)),
    path('<str:executor_id>/', include(router2.urls))
]
