"""Optional, coarse profile fields for civic poll summaries.

Values are states / age bands — not villages, exact ages, or other identifiers.
"""

REGION_UNSPECIFIED = ''
REGION_PREFER_NOT = 'prefer_not'
REGION_OTHER = 'other'

REGION_CHOICES = [
    (REGION_UNSPECIFIED, 'Prefer not to say / not set'),
    ('central_equatoria', 'Central Equatoria'),
    ('eastern_equatoria', 'Eastern Equatoria'),
    ('western_equatoria', 'Western Equatoria'),
    ('jonglei', 'Jonglei'),
    ('unity', 'Unity'),
    ('upper_nile', 'Upper Nile'),
    ('lakes', 'Lakes'),
    ('warrap', 'Warrap'),
    ('northern_bahr_el_ghazal', 'Northern Bahr el Ghazal'),
    ('western_bahr_el_ghazal', 'Western Bahr el Ghazal'),
    (REGION_OTHER, 'Other or outside South Sudan'),
    (REGION_PREFER_NOT, 'Prefer not to say'),
]

AGE_UNSPECIFIED = ''
AGE_PREFER_NOT = 'prefer_not'

AGE_BAND_CHOICES = [
    (AGE_UNSPECIFIED, 'Prefer not to say / not set'),
    ('under_18', 'Under 18'),
    ('18_24', '18–24'),
    ('25_34', '25–34'),
    ('35_49', '35–49'),
    ('50_plus', '50 and over'),
    (AGE_PREFER_NOT, 'Prefer not to say'),
]

REGION_VALUES = {value for value, _label in REGION_CHOICES}
AGE_BAND_VALUES = {value for value, _label in AGE_BAND_CHOICES}
