from django.urls import path

from .views import GamificationLeaderboardView, GamificationMeView

urlpatterns = [
    path('me/', GamificationMeView.as_view(), name='gamification-me'),
    path('leaderboard/', GamificationLeaderboardView.as_view(), name='gamification-leaderboard'),
]
