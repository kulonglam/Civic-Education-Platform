from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework import status

from apps.engagement.models import CivicEvent, EventSignup
from apps.engagement.reminders import send_due_event_reminders
from apps.notifications.models import Notification
from apps.tenants.models import Membership
from tests.conftest import bind_client_to_org


def _make_event(org, **overrides):
    starts = timezone.now() + timedelta(days=14)
    defaults = {
        'organization': org,
        'title': 'Sample civic event',
        'description': 'A published civic event for tests.',
        'location': 'Juba',
        'kind': CivicEvent.KIND_COMMUNITY_MEETING,
        'starts_at': starts,
        'ends_at': starts + timedelta(hours=2),
        'status': CivicEvent.STATUS_PUBLISHED,
        'allows_registration': True,
    }
    defaults.update(overrides)
    return CivicEvent.objects.create(**defaults)


@pytest.mark.django_db
class TestCivicEvents:
    def test_public_list_hides_drafts(self, api_client, org):
        _make_event(org, title='Published meeting')
        _make_event(org, title='Hidden draft', status=CivicEvent.STATUS_DRAFT)
        api_client.credentials(HTTP_X_TENANT_SLUG=org.slug)
        response = api_client.get('/api/events/')
        assert response.status_code == status.HTTP_200_OK
        titles = [row['title'] for row in response.data['results']]
        assert 'Published meeting' in titles
        assert 'Hidden draft' not in titles

    def test_filter_by_kind(self, api_client, org):
        _make_event(org, title='Hearing', kind=CivicEvent.KIND_PUBLIC_HEARING)
        _make_event(org, title='Workshop', kind=CivicEvent.KIND_WORKSHOP)
        api_client.credentials(HTTP_X_TENANT_SLUG=org.slug)
        response = api_client.get('/api/events/', {'kind': 'workshop'})
        titles = [row['title'] for row in response.data['results']]
        assert titles == ['Workshop']

    def test_guest_cannot_register(self, api_client, org):
        event = _make_event(org)
        api_client.credentials(HTTP_X_TENANT_SLUG=org.slug)
        response = api_client.post(f'/api/events/{event.id}/register/', {'registered': True}, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_member_can_register_and_set_reminder(self, api_client, org, citizen_user):
        event = _make_event(org)
        bind_client_to_org(api_client, citizen_user, org, membership_role=Membership.MEMBER, skip_mfa=True)
        response = api_client.post(f'/api/events/{event.id}/register/', {'registered': True}, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['user_registered'] is True
        assert EventSignup.objects.filter(event=event, user=citizen_user, is_registered=True).exists()
        assert Notification.objects.filter(
            user=citizen_user,
            notification_type='event_registration',
        ).exists()

        response = api_client.post(f'/api/events/{event.id}/reminder/', {'reminder': True}, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['user_reminder'] is True
        signup = EventSignup.objects.get(event=event, user=citizen_user)
        assert signup.reminder_enabled is True

    def test_holiday_rejects_registration(self, api_client, org, citizen_user):
        event = _make_event(
            org,
            title='Independence Day',
            kind=CivicEvent.KIND_NATIONAL_HOLIDAY,
            is_all_day=True,
            allows_registration=True,
        )
        bind_client_to_org(api_client, citizen_user, org, membership_role=Membership.MEMBER, skip_mfa=True)
        response = api_client.post(f'/api/events/{event.id}/register/', {'registered': True}, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert EventSignup.objects.filter(event=event, is_registered=True).count() == 0

    def test_calendar_ics_contains_summary_and_start(self, api_client, org):
        event = _make_event(org, title='County hearing')
        api_client.credentials(HTTP_X_TENANT_SLUG=org.slug)
        response = api_client.get(f'/api/events/{event.id}/calendar/')
        assert response.status_code == status.HTTP_200_OK
        body = response.content.decode()
        assert 'BEGIN:VCALENDAR' in body
        assert 'SUMMARY:County hearing' in body
        assert 'DTSTART:' in body

    def test_reminder_task_sends_once(self, org, citizen_user):
        event = _make_event(org, title='Soon meeting', starts_at=timezone.now() + timedelta(hours=6))
        signup = EventSignup.objects.create(
            organization=org,
            event=event,
            user=citizen_user,
            reminder_enabled=True,
        )
        sent = send_due_event_reminders()
        assert sent == 1
        signup.refresh_from_db()
        assert signup.reminder_sent_at is not None
        assert Notification.objects.filter(
            user=citizen_user,
            notification_type='event_reminder',
            title__contains='Soon meeting',
        ).exists()
        assert send_due_event_reminders() == 0
