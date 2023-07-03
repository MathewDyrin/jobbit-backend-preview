from django.urls import path
from . import views


urlpatterns = [
    path('api/v1/user/transactions/', views.Transaction.as_view()),
    path('api/v1/subscription/make/', views.Subscription.as_view()),
    path('api/v1/subscription/plans/', views.SubscriptionPlan.as_view()),
]
