from django.urls import path

from .views import (
    BillingPortalView,
    CheckoutView,
    CurrentSubscriptionView,
    PlanListView,
    StripeWebhookView,
)

urlpatterns = [
    path('plans/', PlanListView.as_view(), name='billing-plans'),
    path('subscription/', CurrentSubscriptionView.as_view(), name='billing-subscription'),
    path('checkout/', CheckoutView.as_view(), name='billing-checkout'),
    path('portal/', BillingPortalView.as_view(), name='billing-portal'),
    path('webhook/', StripeWebhookView.as_view(), name='billing-webhook'),
]
