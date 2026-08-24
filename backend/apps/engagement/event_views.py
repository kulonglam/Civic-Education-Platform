from django.db.models import Count, Prefetch, Q
from django.http import HttpResponse
from django.utils import timezone
from django_filters import rest_framework as filters
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.notifications.fan_out import notify_user
from apps.tenants.permissions import CanDeleteOrgContent, IsOrgContentEditor, IsOrgMember

from .calendar import build_ics
from .models import CivicEvent, EventSignup
from .news_views import _can_see_unpublished
from .reminders import event_is_due_for_reminder, send_event_reminder
from .serializers import CivicEventSerializer, EventRegisterSerializer, EventReminderSerializer


class CivicEventFilter(filters.FilterSet):
    kind = filters.CharFilter()
    status = filters.CharFilter()
    starts_after = filters.IsoDateTimeFilter(field_name='starts_at', lookup_expr='gte')
    starts_before = filters.IsoDateTimeFilter(field_name='starts_at', lookup_expr='lte')

    class Meta:
        model = CivicEvent
        fields = ['kind', 'status']


class CivicEventViewSet(viewsets.ModelViewSet):
    serializer_class = CivicEventSerializer
    filterset_class = CivicEventFilter
    search_fields = ['title', 'title_ar', 'description', 'description_ar', 'location', 'location_ar']
    ordering_fields = ['starts_at', 'created_at', 'title']
    ordering = ['starts_at']
    lookup_field = 'id'

    def get_queryset(self):
        qs = CivicEvent.objects.select_related('created_by').annotate(
            registered_count=Count('signups', filter=Q(signups__is_registered=True)),
        )
        if not _can_see_unpublished(self.request.user):
            qs = qs.filter(status__in=[CivicEvent.STATUS_PUBLISHED, CivicEvent.STATUS_CANCELLED])
        user = self.request.user
        if user and user.is_authenticated:
            qs = qs.prefetch_related(
                Prefetch(
                    'signups',
                    queryset=EventSignup.objects.filter(user=user),
                    to_attr='_my_signups',
                )
            )
        return qs

    def get_permissions(self):
        if self.action in ('list', 'retrieve', 'calendar'):
            return [AllowAny()]
        if self.action in ('register', 'reminder'):
            return [IsAuthenticated(), IsOrgMember()]
        if self.action == 'destroy':
            return [IsAuthenticated(), IsOrgMember(), CanDeleteOrgContent()]
        return [IsAuthenticated(), IsOrgMember(), IsOrgContentEditor()]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def _event_response(self, event):
        event = self.get_queryset().get(pk=event.pk)
        return CivicEventSerializer(event, context={'request': self.request}).data

    def _get_or_create_signup(self, event):
        signup, _ = EventSignup.objects.get_or_create(
            organization=event.organization,
            event=event,
            user=self.request.user,
            defaults={'is_registered': False, 'reminder_enabled': False},
        )
        return signup

    @action(detail=True, methods=['post'])
    def register(self, request, id=None):
        event = self.get_object()
        serializer = EventRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        want_registered = serializer.validated_data['registered']

        if want_registered:
            if event.status == CivicEvent.STATUS_CANCELLED:
                return Response({'detail': 'This event has been cancelled.'}, status=status.HTTP_400_BAD_REQUEST)
            if not event.accepts_registration():
                return Response(
                    {'detail': 'Registration is not available for this event.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            registered_count = event.signups.filter(is_registered=True).count()
            signup = self._get_or_create_signup(event)
            if event.capacity and registered_count >= event.capacity and not signup.is_registered:
                return Response({'detail': 'This event is full.'}, status=status.HTTP_400_BAD_REQUEST)
            if not signup.is_registered:
                signup.is_registered = True
                signup.save(update_fields=['is_registered', 'updated_at'])
                when = timezone.localtime(event.starts_at).strftime('%d %b %Y %H:%M')
                notify_user(
                    user=request.user,
                    notification_type='event_registration',
                    title=f'Registered: {event.title}',
                    message=f'You are registered for {event.title} on {when}.',
                    organization=event.organization,
                )
        else:
            signup = EventSignup.objects.filter(event=event, user=request.user).first()
            if signup and signup.is_registered:
                signup.is_registered = False
                signup.save(update_fields=['is_registered', 'updated_at'])

        return Response(self._event_response(event))

    @action(detail=True, methods=['post'])
    def reminder(self, request, id=None):
        event = self.get_object()
        serializer = EventReminderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        want_reminder = serializer.validated_data['reminder']

        if event.status == CivicEvent.STATUS_CANCELLED and want_reminder:
            return Response(
                {'detail': 'Reminders are not available for cancelled events.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if event.status == CivicEvent.STATUS_DRAFT:
            return Response({'detail': 'Event not found.'}, status=status.HTTP_404_NOT_FOUND)

        signup = self._get_or_create_signup(event)
        signup.reminder_enabled = want_reminder
        updates = ['reminder_enabled', 'updated_at']
        if not want_reminder:
            signup.reminder_sent_at = None
            updates.append('reminder_sent_at')
        signup.save(update_fields=updates)
        if want_reminder and event_is_due_for_reminder(event):
            send_event_reminder(signup)
        elif want_reminder:
            notify_user(
                user=request.user,
                notification_type='event_reminder',
                title=f'Reminder set: {event.title}',
                message=f'We will remind you before {event.title} begins.',
                organization=event.organization,
            )
        return Response(self._event_response(event))

    @action(detail=True, methods=['get'], url_path='calendar')
    def calendar(self, request, id=None):
        event = self.get_object()
        filename = f'{event.id}.ics'
        response = HttpResponse(build_ics(event), content_type='text/calendar; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
