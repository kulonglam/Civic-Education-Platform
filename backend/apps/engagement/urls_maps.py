from django.urls import path

from .map_views import CivicMapView

urlpatterns = [
    path('civic/', CivicMapView.as_view(), name='civic-map'),
]
