"""Tutor exceptions shared by the providers and the service layer."""

from rest_framework.exceptions import APIException


class TutorBudgetExceeded(APIException):
    status_code = 429
    default_detail = 'Daily AI tutor message limit reached. Upgrade your plan for more messages.'
    default_code = 'tutor_budget_exceeded'


class TutorUnavailable(APIException):
    status_code = 503
    default_detail = 'AI tutor is temporarily unavailable.'
    default_code = 'tutor_unavailable'
