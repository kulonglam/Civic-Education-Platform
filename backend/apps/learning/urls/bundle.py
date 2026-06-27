from django.urls import path
from ..views import content_bundle

urlpatterns = [
    path('', content_bundle, name='content-bundle'),
]
