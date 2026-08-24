from datetime import timedelta

from django.db.models import Count
from django.utils import timezone
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import UserProfile
from apps.analytics.services import MIN_BUCKET_COUNT, org_member_users
from apps.tenants.context import get_current_organization

from .maps import MAP_STATE_KEYS, REGION_CENTROIDS, REGION_LABELS
from .models import CivicEvent


def _event_payload(event) -> dict:
    lon, lat = None, None
    if event.longitude is not None and event.latitude is not None:
        lon = float(event.longitude)
        lat = float(event.latitude)
    elif event.region in REGION_CENTROIDS:
        lon, lat = REGION_CENTROIDS[event.region]
    return {
        'id': str(event.id),
        'title': event.title,
        'title_ar': event.title_ar,
        'kind': event.kind,
        'location': event.location,
        'region': event.region or '',
        'starts_at': event.starts_at,
        'status': event.status,
        'longitude': lon,
        'latitude': lat,
    }


@extend_schema(responses=OpenApiTypes.OBJECT)
class CivicMapView(APIView):
    """Published civic events and k-anonymized learner counts by state."""

    permission_classes = [AllowAny]

    def get(self, request):
        now = timezone.now()
        events = list(
            CivicEvent.objects.filter(
                status__in=[CivicEvent.STATUS_PUBLISHED, CivicEvent.STATUS_CANCELLED],
                starts_at__gte=now - timedelta(days=14),
            ).order_by('starts_at')[:80]
        )
        upcoming = [event for event in events if event.starts_at >= now and event.status == CivicEvent.STATUS_PUBLISHED]

        event_counts = {key: 0 for key in MAP_STATE_KEYS}
        nationwide = 0
        for event in upcoming:
            if event.region in event_counts:
                event_counts[event.region] += 1
            else:
                nationwide += 1

        learner_counts = {key: 0 for key in MAP_STATE_KEYS}
        organization = get_current_organization()
        if organization is not None:
            members = org_member_users()
            for row in (
                UserProfile.objects.filter(user__in=members, region__in=MAP_STATE_KEYS)
                .values('region')
                .annotate(total=Count('id'))
            ):
                learner_counts[row['region']] = row['total']

        regions = []
        for key in MAP_STATE_KEYS:
            learners = learner_counts[key]
            hidden = learners < MIN_BUCKET_COUNT
            lon, lat = REGION_CENTROIDS[key]
            regions.append({
                'key': key,
                'label': REGION_LABELS.get(key, key),
                'centroid': [lon, lat],
                'upcoming_event_count': event_counts[key],
                'learner_count': None if hidden else learners,
                'learner_count_hidden': hidden,
            })

        return Response({
            'regions': regions,
            'nationwide_upcoming_count': nationwide,
            'events': [_event_payload(event) for event in events],
            'privacy': {'min_region_learners': MIN_BUCKET_COUNT},
        })
