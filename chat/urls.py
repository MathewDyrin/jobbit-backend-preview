from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('', views.ChatViewSet, basename='chat')

router2 = DefaultRouter()
router2.register('participant', views.ParticipantViewSet, basename='participant')
router2.register('message', views.MessageViewSet, basename='message')

urlpatterns = [
    path('', include(router.urls)),
    path('<str:chat_id>/', include(router2.urls))
]
