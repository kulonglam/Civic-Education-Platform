import logging

from django.conf import settings
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import generics, serializers, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.security import log_security_event
from apps.tenants.context import get_current_organization
from apps.tenants.permissions import IsOrgMember, IsOrgOwnerOrAdmin

from .models import Plan, Subscription
from .providers import get_billing_provider
from .serializers import CheckoutSerializer, PlanSerializer, SubscriptionSerializer
from .services import (
    apply_checkout_completed,
    apply_subscription_deleted,
    apply_subscription_updated,
    ensure_subscription,
    get_subscription,
    self_serve_checkout_enabled,
    usage_summary,
)

logger = logging.getLogger(__name__)


class PlanListView(generics.ListAPIView):
    serializer_class = PlanSerializer
    permission_classes = [AllowAny]
    queryset = Plan.objects.filter(is_active=True)


class CurrentSubscriptionView(APIView):
    permission_classes = [IsAuthenticated, IsOrgMember]
    serializer_class = SubscriptionSerializer

    def get(self, request):
        organization = get_current_organization()
        subscription = ensure_subscription(organization)
        if subscription is None:
            return Response(
                {'detail': 'Billing is not configured. Run seed_data to create plans.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        return Response({
            'subscription': SubscriptionSerializer(subscription).data,
            'usage': usage_summary(organization),
            'self_serve_checkout': self_serve_checkout_enabled(),
        })


class CheckoutView(APIView):
    permission_classes = [IsAuthenticated, IsOrgOwnerOrAdmin]
    serializer_class = CheckoutSerializer

    @extend_schema(
        request=CheckoutSerializer,
        responses=inline_serializer(
            name='CheckoutResponse',
            fields={'checkout_url': serializers.CharField()},
        ),
    )
    def post(self, request):
        organization = get_current_organization()
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        plan = Plan.objects.filter(code=serializer.validated_data['plan_code'], is_active=True).first()
        if plan is None:
            return Response({'detail': 'Unknown plan.'}, status=status.HTTP_404_NOT_FOUND)

        subscription = ensure_subscription(organization)
        if subscription is None:
            return Response(
                {'detail': 'Billing is not configured.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        if subscription.plan_id == plan.id and subscription.is_current:
            return Response({'detail': 'Organization is already on this plan.'}, status=status.HTTP_400_BAD_REQUEST)

        if plan.price_cents == 0:
            subscription.plan = plan
            subscription.status = Subscription.ACTIVE
            subscription.save(update_fields=['plan', 'status'])
            return Response({'checkout_url': f'{settings.FRONTEND_URL}/billing?status=success'})

        if not self_serve_checkout_enabled():
            return Response(
                {
                    'detail': (
                        'Paid plans are assigned by the platform operator '
                        '(invoice or card upgrade). Self-serve checkout is disabled.'
                    ),
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        provider = get_billing_provider()
        if not subscription.provider_customer_id:
            subscription.provider_customer_id = provider.create_customer(organization, request.user.email)
            subscription.save(update_fields=['provider_customer_id'])

        base = settings.FRONTEND_URL
        result = provider.create_checkout_session(
            subscription, plan,
            success_url=f'{base}/billing?status=success',
            cancel_url=f'{base}/billing?status=cancel',
        )

        if result.activate_immediately:
            subscription.plan = plan
            subscription.status = Subscription.ACTIVE
            subscription.save(update_fields=['plan', 'status'])

        return Response({'checkout_url': result.url})


class BillingPortalView(APIView):
    permission_classes = [IsAuthenticated, IsOrgOwnerOrAdmin]
    serializer_class = SubscriptionSerializer

    @extend_schema(
        request=None,
        responses=inline_serializer(
            name='PortalResponse',
            fields={'portal_url': serializers.CharField()},
        ),
    )
    def post(self, request):
        organization = get_current_organization()
        subscription = get_subscription(organization)
        if subscription is None or not subscription.provider_customer_id:
            return Response(
                {'detail': 'No billing account found for this organization.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        provider = get_billing_provider()
        url = provider.create_portal_session(subscription, return_url=f'{settings.FRONTEND_URL}/billing')
        return Response({'portal_url': url})


class StripeWebhookView(APIView):
    """Receives Stripe events to keep subscription state in sync."""

    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(request=OpenApiTypes.OBJECT, responses=OpenApiTypes.OBJECT)
    def post(self, request):
        provider = get_billing_provider()
        signature = request.META.get('HTTP_STRIPE_SIGNATURE', '')
        try:
            event = provider.parse_webhook(request.body, signature)
        except Exception as exc:  # noqa: BLE001
            logger.warning('Invalid billing webhook: %s', exc)
            log_security_event(
                'billing_webhook_invalid',
                request=request,
                detail={'error': str(exc)},
            )
            return Response({'detail': 'Invalid payload.'}, status=status.HTTP_400_BAD_REQUEST)

        self._handle_event(event)
        return Response({'received': True})

    def _handle_event(self, event: dict):
        event_type = event.get('type')
        data = (event.get('data') or {}).get('object', {})

        if event_type == 'checkout.session.completed':
            apply_checkout_completed(data)
        elif event_type == 'customer.subscription.updated':
            apply_subscription_updated(data)
        elif event_type == 'customer.subscription.deleted':
            apply_subscription_deleted(data)
