from django.urls import path

from ..recommendation_views import RecommendationView

urlpatterns = [
    path('', RecommendationView.as_view(), name='learning-recommendations'),
]
