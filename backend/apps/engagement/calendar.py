"""ICS and Google Calendar helpers for civic events."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone as dt_timezone
from urllib.parse import urlencode

from django.utils import timezone


def ics_escape(value: str) -> str:
    return (
        (value or '')
        .replace('\\', '\\\\')
        .replace(';', '\\;')
        .replace(',', '\\,')
        .replace('\r\n', '\n')
        .replace('\n', '\\n')
    )


def fold_ics_line(line: str) -> str:
    if len(line) <= 75:
        return line
    chunks = [line[:75]]
    rest = line[75:]
    while rest:
        chunks.append(' ' + rest[:74])
        rest = rest[74:]
    return '\r\n'.join(chunks)


def _as_aware(dt: datetime) -> datetime:
    if timezone.is_naive(dt):
        return timezone.make_aware(dt, timezone.get_current_timezone())
    return dt


def fmt_utc(dt: datetime) -> str:
    return _as_aware(dt).astimezone(dt_timezone.utc).strftime('%Y%m%dT%H%M%SZ')


def _all_day_dates(event) -> tuple[str, str]:
    start = timezone.localtime(_as_aware(event.starts_at)).date()
    end = timezone.localtime(_as_aware(event.ends_at or event.starts_at)).date()
    exclusive_end = end + timedelta(days=1)
    return start.strftime('%Y%m%d'), exclusive_end.strftime('%Y%m%d')


def event_time_span(event) -> tuple[datetime, datetime]:
    start = _as_aware(event.starts_at)
    end = _as_aware(event.ends_at) if event.ends_at else start + timedelta(hours=1)
    if end < start:
        end = start + timedelta(hours=1)
    return start, end


def build_ics(event) -> str:
    uid = f'{event.id}@civic-education.ss'
    stamp = fmt_utc(timezone.now())
    status = 'CANCELLED' if event.status == event.STATUS_CANCELLED else 'CONFIRMED'
    lines = [
        'BEGIN:VCALENDAR',
        'VERSION:2.0',
        'PRODID:-//Civic Education RSS//Civic Events//EN',
        'CALSCALE:GREGORIAN',
        'METHOD:PUBLISH',
        'BEGIN:VEVENT',
        f'UID:{uid}',
        f'DTSTAMP:{stamp}',
        f'STATUS:{status}',
    ]
    if event.is_all_day:
        start_date, end_date = _all_day_dates(event)
        lines.append(f'DTSTART;VALUE=DATE:{start_date}')
        lines.append(f'DTEND;VALUE=DATE:{end_date}')
    else:
        start, end = event_time_span(event)
        lines.append(f'DTSTART:{fmt_utc(start)}')
        lines.append(f'DTEND:{fmt_utc(end)}')
    lines.append(f'SUMMARY:{ics_escape(event.title)}')
    if event.description:
        lines.append(f'DESCRIPTION:{ics_escape(event.description)}')
    if event.location:
        lines.append(f'LOCATION:{ics_escape(event.location)}')
    lines.extend(['END:VEVENT', 'END:VCALENDAR'])
    return '\r\n'.join(fold_ics_line(line) for line in lines) + '\r\n'


def google_calendar_url(event) -> str:
    if event.is_all_day:
        start_date, end_date = _all_day_dates(event)
        dates = f'{start_date}/{end_date}'
    else:
        start, end = event_time_span(event)
        dates = f'{fmt_utc(start)}/{fmt_utc(end)}'
    params = {
        'action': 'TEMPLATE',
        'text': event.title or '',
        'dates': dates,
        'details': event.description or '',
        'location': event.location or '',
    }
    return 'https://calendar.google.com/calendar/render?' + urlencode(params)
