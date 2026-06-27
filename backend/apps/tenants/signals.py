"""Tenant signal handlers.

Subscription provisioning on organization creation lives in the billing app
(see ``apps.billing.signals``) to keep tenancy and billing decoupled.
"""
