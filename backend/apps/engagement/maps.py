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

# Geographic centres (longitude, latitude) from geoBoundaries SSD ADM1 2020.
REGION_CENTROIDS = {
    'central_equatoria': (31.19, 4.77),
    'eastern_equatoria': (33.60, 4.90),
    'western_equatoria': (28.68, 5.55),
    'jonglei': (32.33, 7.39),
    'unity': (29.89, 8.93),
    'upper_nile': (32.80, 9.90),
    'lakes': (29.94, 6.64),
    'warrap': (28.73, 8.14),
    'northern_bahr_el_ghazal': (27.04, 8.88),
    'western_bahr_el_ghazal': (26.22, 8.23),
}

EVENT_REGION_CHOICES = [
    ('', 'Nationwide / not specified'),
    *[(key, REGION_LABELS[key]) for key in MAP_STATE_KEYS],
    ('other', REGION_LABELS.get('other', 'Other')),
]

EVENT_REGION_VALUES = {value for value, _label in EVENT_REGION_CHOICES}
