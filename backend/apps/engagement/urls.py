from django.urls import path

from .views import (
    CampaignListCreateView,
    PetitionListCreateView,
    PetitionSignView,
    PollListCreateView,
    PollVoteView,
)

urlpatterns = [
    path('polls/', PollListCreateView.as_view(), name='engagement-polls'),
    path('polls/<uuid:poll_id>/vote/', PollVoteView.as_view(), name='engagement-poll-vote'),
    path('petitions/', PetitionListCreateView.as_view(), name='engagement-petitions'),
    path('petitions/<uuid:petition_id>/sign/', PetitionSignView.as_view(), name='engagement-petition-sign'),
    path('campaigns/', CampaignListCreateView.as_view(), name='engagement-campaigns'),
]
