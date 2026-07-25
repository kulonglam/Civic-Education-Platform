from django.urls import path

from .views import GamificationMeView

urlpatterns = [
    path('me/', GamificationMeView.as_view(), name='gamification-me'),
]
