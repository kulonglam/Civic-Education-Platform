"""Pluggable billing providers.

The ``dummy`` provider requires no external service or API keys and is used in
development/testing: a checkout immediately activates the chosen plan. The
``stripe`` provider integrates with Stripe Checkout + Billing Portal and is
used when ``BILLING_PROVIDER=stripe`` and ``STRIPE_SECRET_KEY`` is configured.
"""

import uuid

from django.conf import settings


class CheckoutResult:
    def __init__(self, url: str, activate_immediately: bool = False):
        self.url = url
        self.activate_immediately = activate_immediately


class BaseBillingProvider:
    def create_customer(self, organization, email: str) -> str:
        raise NotImplementedError

    def create_checkout_session(self, subscription, plan, success_url, cancel_url) -> CheckoutResult:
        raise NotImplementedError

    def create_portal_session(self, subscription, return_url) -> str:
        raise NotImplementedError

    def parse_webhook(self, payload: bytes, signature: str) -> dict:
        raise NotImplementedError


class DummyBillingProvider(BaseBillingProvider):
    """No-op provider for local dev/tests; activates plans instantly."""

    def create_customer(self, organization, email: str) -> str:
        return f'dummy_cus_{organization.id}'

    def create_checkout_session(self, subscription, plan, success_url, cancel_url) -> CheckoutResult:
        return CheckoutResult(url=success_url, activate_immediately=True)

    def create_portal_session(self, subscription, return_url) -> str:
        return return_url

    def parse_webhook(self, payload: bytes, signature: str) -> dict:
        import json

        try:
            return json.loads(payload or b'{}')
        except (ValueError, TypeError):
            return {}


class StripeBillingProvider(BaseBillingProvider):
    def __init__(self):
        import stripe

        stripe.api_key = settings.STRIPE_SECRET_KEY
        self._stripe = stripe

    def create_customer(self, organization, email: str) -> str:
        customer = self._stripe.Customer.create(
            email=email,
            name=organization.name,
            metadata={'organization_id': str(organization.id)},
        )
        return customer['id']

    def create_checkout_session(self, subscription, plan, success_url, cancel_url) -> CheckoutResult:
        price_id = settings.STRIPE_PRICE_IDS.get(plan.code)
        if not price_id:
            raise ValueError(f'No Stripe price configured for plan "{plan.code}".')
        session = self._stripe.checkout.Session.create(
            mode='subscription',
            customer=subscription.provider_customer_id or None,
            line_items=[{'price': price_id, 'quantity': 1}],
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                'organization_id': str(subscription.organization_id),
                'plan_code': plan.code,
            },
            subscription_data={
                'metadata': {
                    'organization_id': str(subscription.organization_id),
                    'plan_code': plan.code,
                },
            },
        )
        return CheckoutResult(url=session['url'], activate_immediately=False)

    def create_portal_session(self, subscription, return_url) -> str:
        session = self._stripe.billing_portal.Session.create(
            customer=subscription.provider_customer_id,
            return_url=return_url,
        )
        return session['url']

    def parse_webhook(self, payload: bytes, signature: str) -> dict:
        return self._stripe.Webhook.construct_event(
            payload, signature, settings.STRIPE_WEBHOOK_SECRET
        )


def get_billing_provider() -> BaseBillingProvider:
    provider = getattr(settings, 'BILLING_PROVIDER', 'dummy')
    if provider == 'stripe':
        return StripeBillingProvider()
    return DummyBillingProvider()
