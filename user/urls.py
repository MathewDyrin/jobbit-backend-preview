from django.urls import path
from django.urls import include
from rest_framework.routers import DefaultRouter

from .views import UserViewSet
from .views import TokenObtainPairViewSet
from .views import TokenDestroyView
from .views import TokenRefreshView
from .views import DjoserUserOverride
from .views import UserOAuth2Providers

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register('token', TokenObtainPairViewSet, basename='token')
router.register('provider', UserOAuth2Providers, basename='provider')

djoser_router = DefaultRouter()
djoser_router.register('users', DjoserUserOverride)

urlpatterns = [
    path('api/v1/auth/', include(djoser_router.urls)),
    path('api/v1/', include(router.urls)),
    path('api/v1/token/destroy/', TokenDestroyView.as_view(), name='token_destroy'),
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
]
