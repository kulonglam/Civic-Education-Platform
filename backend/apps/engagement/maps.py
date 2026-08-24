"""South Sudan state metadata for the civic map.

Polygons live on the frontend; this module supplies stable keys, labels, and
centroids used to pin events that have a region but no exact coordinates.
"""

from apps.accounts.demographics import REGION_CHOICES

MAP_STATE_KEYS = (
    'central_equatoria',
    'eastern_equatoria',
    'western_equatoria',
    'jonglei',
    'unity',
    'upper_nile',
    'lakes',
    'warrap',
    'northern_bahr_el_ghazal',
    'western_bahr_el_ghazal',
)

REGION_LABELS = {value: label for value, label in REGION_CHOICES}

# Approximate geographic centres (longitude, latitude) for map pins.
REGION_CENTROIDS = {
    'central_equatoria': (31.58, 4.85),
    'eastern_equatoria': (33.40, 4.55),
    'western_equatoria': (28.40, 5.35),
    'jonglei': (32.10, 7.20),
    'unity': (29.80, 9.10),
    'upper_nile': (32.90, 10.20),
    'lakes': (29.70, 6.80),
    'warrap': (28.15, 8.05),
    'northern_bahr_el_ghazal': (26.70, 8.95),
    'western_bahr_el_ghazal': (25.90, 7.70),
}

EVENT_REGION_CHOICES = [
    ('', 'Nationwide / not specified'),
    *[(key, REGION_LABELS[key]) for key in MAP_STATE_KEYS],
    ('other', REGION_LABELS.get('other', 'Other')),
]

EVENT_REGION_VALUES = {value for value, _label in EVENT_REGION_CHOICES}
